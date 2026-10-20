"""Turn Falco Kubernetes audit events into concise, readable messages."""

from collections.abc import Mapping
import os
from typing import Any


_MISSING = {"", "<na>", "<nil>", "nil", "none", "null"}

_VERBS = {
    "create": "Tạo",
    "update": "Cập nhật",
    "patch": "Cập nhật",
    "delete": "Xóa",
    "deletecollection": "Xóa hàng loạt",
    "get": "Xem",
    "list": "Liệt kê",
    "watch": "Theo dõi",
    "exec": "Mở phiên lệnh trong",
    "attach": "Kết nối vào",
    "connect": "Kết nối tới",
}

_RESOURCE_NAMES = {
    "configmaps": "ConfigMap",
    "cronjobs": "CronJob",
    "daemonsets": "DaemonSet",
    "deployments": "Deployment",
    "jobs": "Job",
    "namespaces": "Namespace",
    "pods": "Pod",
    "replicasets": "ReplicaSet",
    "secrets": "Secret",
    "services": "Service",
    "statefulsets": "StatefulSet",
}


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if text.lower() in _MISSING else text


def _first(fields: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = _clean(fields.get(key))
        if value:
            return value
    return None


def _resource_name(resource: str | None) -> str | None:
    if not resource:
        return None
    return _RESOURCE_NAMES.get(resource.lower(), resource.rstrip("s").capitalize())


def _outcome(fields: Mapping[str, Any]) -> str:
    code = _first(fields, "ka.response.code")
    if not code:
        return "Không rõ"
    try:
        status = int(code)
    except ValueError:
        return f"Mã {code}"
    return "✅ Thành công" if 200 <= status < 300 or status == 101 else f"❌ Thất bại (HTTP {status})"


def _actor(fields: Mapping[str, Any]) -> str | None:
    # For Rancher impersonation, the impersonated human is more useful than
    # the Rancher service account that proxied the request.
    return _first(
        fields,
        "jevt.value[/impersonatedUser/extra/username/0]",
        "ka.impuser.name",
        "ka.user.name",
    )


def format_message(event: Mapping[str, Any]) -> str:
    """Format a Falco event in a compact Alertmanager-like layout."""
    fields_value = event.get("output_fields") or {}
    fields = fields_value if isinstance(fields_value, Mapping) else {}

    rule = _clean(event.get("rule")) or "Falco Alert"
    rule_lower = rule.lower()
    namespace = _first(fields, "ka.target.namespace", "k8s.ns.name")
    resource = _first(fields, "ka.target.resource")
    name = _first(fields, "ka.target.name")
    verb = _first(fields, "ka.verb")
    actor = _actor(fields)
    outcome = _outcome(fields)
    priority = _clean(event.get("priority")) or "Warning"
    severity = priority.upper()
    cluster = _first(fields, "k8s.cluster.name", "cluster.name") or _clean(event.get("cluster")) or os.getenv("CLUSTER_NAME", "Kubernetes")
    started = _clean(event.get("time"))

    if "secret" in rule_lower:
        title = "Truy cập Secret"
        action = _VERBS.get((verb or "").lower(), "Truy cập")
        details = [f"Hành động: {action} Secret"]
        if name:
            details.append(f"Đối tượng: Secret/{name}")
    elif "portforward" in rule_lower or "port-forward" in rule_lower:
        title = "Port-forward Pod"
        details = [f"Đối tượng: Pod/{name}"] if name else []
    elif "scale workload" in rule_lower:
        title = "Điều chỉnh quy mô workload"
        kind = _resource_name(resource) or "Workload"
        details = [f"Đối tượng: {kind}/{name}" if name else f"Đối tượng: {kind}"]
        details.append("Hành động: Thay đổi số replica")
        replicas = _first(fields, "jevt.value[/requestObject/spec/replicas]")
        if replicas:
            details.append(f"Số replica mong muốn: {replicas}")
    elif "rollout restart" in rule_lower:
        title = "Yêu cầu rollout restart"
        kind = _resource_name(resource) or "Workload"
        details = [f"Đối tượng: {kind}/{name}" if name else f"Đối tượng: {kind}"]
        details.append("Hành động: Khởi động lại workload")
    elif "workload" in rule_lower:
        title = "Thay đổi workload"
        kind = _resource_name(resource) or "Workload"
        details = [f"Đối tượng: {kind}/{name}" if name else f"Đối tượng: {kind}"]
        details.append(f"Hành động: {_VERBS.get((verb or '').lower(), verb or 'Thay đổi')}")
    else:
        title = rule
        details = []
        if resource or name:
            kind = _resource_name(resource) or "Tài nguyên"
            details.append(f"Đối tượng: {kind}/{name}" if name else f"Đối tượng: {kind}")
        if verb:
            details.append(f"Hành động: {_VERBS.get(verb.lower(), verb)}")

    lines = [
        f"🚨 [FIRING: {severity}] {title}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"Severity: {severity}",
        f"Cluster: {cluster}",
        f"Namespace: {namespace or 'không rõ'}",
        "",
        "Details:",
        *[f"• {detail}" for detail in details],
    ]
    if actor:
        lines.append(f"• Người dùng: {actor}")
    if any(token in rule_lower for token in ("rollout restart", "scale workload", "workload change")) and outcome == "Không rõ":
        outcome = "✅ Yêu cầu đã được API chấp nhận"
    lines.append(f"• Kết quả: {outcome}")
    if started:
        lines.extend(["", f"Started: {started}"])
    return "\n".join(lines)

