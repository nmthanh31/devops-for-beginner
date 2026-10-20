"""Track Kubernetes workload changes after Falco audit events."""

import asyncio
import logging
import os
from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx


logger = logging.getLogger("falco-router.rollout")
SERVICE_ACCOUNT_DIR = Path("/var/run/secrets/kubernetes.io/serviceaccount")
RESOURCE_API_PATHS = {
    "pods": "/api/v1",
    "deployments": "/apis/apps/v1",
    "statefulsets": "/apis/apps/v1",
    "daemonsets": "/apis/apps/v1",
    "replicasets": "/apis/apps/v1",
    "jobs": "/apis/batch/v1",
}


def workload_complete(resource: str, workload: Mapping[str, Any]) -> bool:
    """Return true when a supported workload has reached its ready/terminal state."""
    metadata = workload.get("metadata") or {}
    spec = workload.get("spec") or {}
    status = workload.get("status") or {}
    if resource in {"deployments", "statefulsets", "daemonsets", "replicasets"}:
        generation = int(metadata.get("generation") or 0)
        observed = int(status.get("observedGeneration") or 0)
        if observed < generation:
            return False

    if resource == "deployments":
        desired = int(spec.get("replicas", 1))
        return (
            int(status.get("updatedReplicas") or 0) >= desired
            and int(status.get("availableReplicas") or 0) >= desired
        )
    if resource == "statefulsets":
        desired = int(spec.get("replicas", 1))
        partition = int(
            ((spec.get("updateStrategy") or {}).get("rollingUpdate") or {}).get("partition") or 0
        )
        updated_target = max(0, desired - partition)
        return (
            int(status.get("updatedReplicas") or 0) >= updated_target
            and int(status.get("readyReplicas") or 0) >= desired
        )
    if resource == "daemonsets":
        desired = int(status.get("desiredNumberScheduled") or 0)
        return (
            int(status.get("updatedNumberScheduled") or 0) >= desired
            and int(status.get("numberAvailable") or 0) >= desired
        )
    if resource == "replicasets":
        desired = int(spec.get("replicas", 1))
        return int(status.get("readyReplicas") or 0) >= desired
    if resource == "pods":
        phase = (status.get("phase") or "").lower()
        conditions = status.get("conditions") or []
        ready = any(
            item.get("type") == "Ready" and item.get("status") == "True"
            for item in conditions
            if isinstance(item, Mapping)
        )
        return phase == "succeeded" or (phase == "running" and ready)
    if resource == "jobs":
        conditions = status.get("conditions") or []
        return any(
            item.get("type") in {"Complete", "Failed"} and item.get("status") == "True"
            for item in conditions
            if isinstance(item, Mapping)
        )
    return False


class WorkloadMonitor:
    def __init__(
        self,
        send: Callable[[str], Awaitable[None]],
        poll_seconds: float = 5.0,
        timeout_seconds: float = 600.0,
    ) -> None:
        self._send = send
        self._poll_seconds = poll_seconds
        self._timeout_seconds = timeout_seconds
        self._tasks: dict[tuple[str, str, str], asyncio.Task[None]] = {}
        self._client: httpx.AsyncClient | None = None

    def _make_client(self) -> httpx.AsyncClient:
        base_url = os.getenv("K8S_API_URL")
        if not base_url:
            host = os.getenv("KUBERNETES_SERVICE_HOST")
            port = os.getenv("KUBERNETES_SERVICE_PORT_HTTPS", "443")
            if not host:
                raise RuntimeError("Kubernetes API service host is unavailable")
            base_url = f"https://{host}:{port}"

        token_path = Path(os.getenv("K8S_TOKEN_FILE", str(SERVICE_ACCOUNT_DIR / "token")))
        ca_path = Path(os.getenv("K8S_CA_FILE", str(SERVICE_ACCOUNT_DIR / "ca.crt")))
        headers: dict[str, str] = {}
        verify: bool | str = True
        if token_path.is_file():
            token = token_path.read_text(encoding="utf-8").strip()
            if token:
                headers["Authorization"] = f"Bearer {token}"
            if ca_path.is_file():
                verify = str(ca_path)
        return httpx.AsyncClient(
            base_url=base_url.rstrip("/"), headers=headers, verify=verify, timeout=8.0
        )

    def track(self, event: Mapping[str, Any]) -> None:
        rule = str(event.get("rule") or "").lower()
        if not any(token in rule for token in ("rollout restart", "scale workload", "workload change")):
            return
        fields = event.get("output_fields")
        if not isinstance(fields, Mapping):
            return
        namespace = fields.get("ka.target.namespace")
        resource = fields.get("ka.target.resource")
        name = fields.get("ka.target.name")
        if not all(isinstance(item, str) and item for item in (namespace, resource, name)):
            logger.warning("workload event lacks target namespace/resource/name; cannot track")
            return
        resource = resource.lower()
        if resource not in RESOURCE_API_PATHS:
            logger.info("no asynchronous status monitor for workload resource=%s", resource)
            return
        verb = str(fields.get("ka.verb") or "").lower()
        if verb not in {"create", "update", "patch", "delete"}:
            logger.info("no asynchronous status monitor for verb=%s", verb)
            return
        if "cronjobs" == resource:
            logger.info("CronJob object accepted; its future scheduled Job is not awaited")
            return

        key = (namespace, resource, name)
        current = self._tasks.get(key)
        if current and not current.done():
            logger.info("rollout is already being tracked namespace=%s resource=%s name=%s", *key)
            return
        task = asyncio.create_task(self._watch(*key, event))
        self._tasks[key] = task

    async def _watch(
        self, namespace: str, resource: str, name: str, event: Mapping[str, Any]
    ) -> None:
        key = (namespace, resource, name)
        started = asyncio.get_running_loop().time()
        cluster = os.getenv("CLUSTER_NAME", "Kubernetes")
        actor = None
        event_time = event.get("time")
        fields = event.get("output_fields")
        if isinstance(fields, Mapping):
            actor = fields.get("ka.impuser.name") or fields.get("ka.user.name")
        verb = str(fields.get("ka.verb") or "").lower() if isinstance(fields, Mapping) else ""
        is_delete = verb == "delete"

        try:
            if self._client is None:
                self._client = self._make_client()
            path = (
                f"{RESOURCE_API_PATHS[resource]}/namespaces/{quote(namespace, safe='')}/"
                f"{quote(resource, safe='')}/{quote(name, safe='')}"
            )
            while asyncio.get_running_loop().time() - started < self._timeout_seconds:
                try:
                    response = await self._client.get(path)
                    if response.status_code == 404 and is_delete:
                        await self._notify(namespace, resource, name, "✅", "Đã xóa khỏi Kubernetes API", actor, cluster, event_time)
                        return
                    if response.status_code in (401, 403):
                        response.raise_for_status()
                    response.raise_for_status()
                    workload = response.json()
                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code
                    if status in (401, 403):
                        reason = "không thể theo dõi (không có quyền hoặc workload không còn tồn tại)"
                        await self._notify(namespace, resource, name, "⚠️", reason, actor, cluster, event_time)
                        return
                    if status == 404 and not is_delete:
                        logger.info("workload not visible yet; retrying status lookup")
                        await asyncio.sleep(self._poll_seconds)
                        continue
                    logger.warning("temporary Kubernetes API error tracking workload: HTTP %s", status)
                    await asyncio.sleep(self._poll_seconds)
                    continue
                except (httpx.HTTPError, ValueError) as exc:
                    logger.warning("temporary error reading workload status: %s", type(exc).__name__)
                    await asyncio.sleep(self._poll_seconds)
                    continue

                if self._workload_failed(resource, workload):
                    await self._notify(
                        namespace, resource, name, "❌", self._failure_message(resource),
                        actor, cluster, event_time,
                    )
                    return
                if workload_complete(resource, workload):
                    message = "Workload đã đạt trạng thái sẵn sàng/hoàn tất"
                    if resource in {"deployments", "statefulsets", "daemonsets", "replicasets"}:
                        message = "Workload đã cập nhật; các replica mới sẵn sàng"
                    await self._notify(namespace, resource, name, "✅", message, actor, cluster, event_time)
                    return
                await asyncio.sleep(self._poll_seconds)

            await self._notify(namespace, resource, name, "⏳", "Workload chưa đạt trạng thái mong muốn sau 10 phút", actor, cluster, event_time)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("rollout monitor failed: %s", type(exc).__name__)
        finally:
            if self._tasks.get(key) is asyncio.current_task():
                self._tasks.pop(key, None)

    @staticmethod
    def _workload_failed(resource: str, workload: Mapping[str, Any]) -> bool:
        if resource == "deployments" and WorkloadMonitor._deployment_failed(workload):
            return True
        if resource == "pods" and ((workload.get("status") or {}).get("phase") == "Failed"):
            return True
        if resource == "jobs":
            conditions = (workload.get("status") or {}).get("conditions") or []
            return any(
                item.get("type") == "Failed" and item.get("status") == "True"
                for item in conditions
                if isinstance(item, Mapping)
            )
        return False

    @staticmethod
    def _failure_message(resource: str) -> str:
        if resource == "deployments":
            return "Deployment rollout thất bại: vượt quá thời hạn tiến triển"
        if resource == "jobs":
            return "Job đã chuyển sang trạng thái Failed"
        if resource == "pods":
            return "Pod đã chuyển sang trạng thái Failed"
        return "Workload chưa đạt trạng thái mong muốn"

    @staticmethod
    def _deployment_failed(workload: Mapping[str, Any]) -> bool:
        metadata = workload.get("metadata") or {}
        status = workload.get("status") or {}
        if int(status.get("observedGeneration") or 0) < int(metadata.get("generation") or 0):
            return False
        conditions = status.get("conditions") or []
        return any(
            item.get("type") == "Progressing"
            and item.get("status") == "False"
            and item.get("reason") == "ProgressDeadlineExceeded"
            for item in conditions
            if isinstance(item, Mapping)
        )

    async def _notify(
        self,
        namespace: str,
        resource: str,
        name: str,
        icon: str,
        result: str,
        actor: Any,
        cluster: str,
        started: Any,
    ) -> None:
        kind = {
            "pods": "Pod", "deployments": "Deployment", "statefulsets": "StatefulSet",
            "daemonsets": "DaemonSet", "replicasets": "ReplicaSet", "jobs": "Job",
        }[resource]
        succeeded = icon == "✅"
        status = "RESOLVED" if succeeded else "FIRING"
        lines = [
            f"{icon} [{status}: {'INFO' if succeeded else 'WARNING'}] Workload {'đã ổn định' if succeeded else 'cần kiểm tra'}: {kind}/{name}",
            "━━━━━━━━━━━━━━━━━━━━",
            "Severity: INFO" if succeeded else "Severity: WARNING",
            f"Cluster: {cluster}",
            f"Namespace: {namespace}",
            "",
            "Details:",
            f"• Đối tượng: {kind}/{name}",
        ]
        if actor:
            lines.append(f"• Người yêu cầu: {actor}")
        lines.extend([f"• Trạng thái: {result}"])
        if started:
            lines.append(f"• Bắt đầu: {started}")
        lines.extend(["", f"Finished: {datetime.now(timezone.utc).isoformat(timespec='seconds')}"])
        await self._send("\n".join(lines))

    async def close(self) -> None:
        tasks = list(self._tasks.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        if self._client is not None:
            await self._client.aclose()
            self._client = None
