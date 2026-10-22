"""Small namespace metadata cache using the Kubernetes REST API and httpx."""

import asyncio
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import httpx


SERVICE_ACCOUNT_DIR = Path("/var/run/secrets/kubernetes.io/serviceaccount")
TOKEN_PATH = SERVICE_ACCOUNT_DIR / "token"
CA_PATH = SERVICE_ACCOUNT_DIR / "ca.crt"


class NamespaceApiUnavailable(RuntimeError):
    """Kubernetes API could not be queried; caller should retry the event."""


class NamespaceCache:
    def __init__(self, refresh_seconds: int = 60) -> None:
        self.refresh_seconds = refresh_seconds
        self._labels: dict[str, dict[str, str]] = {}
        self._refreshed_at = 0.0
        self._lock = asyncio.Lock()
        self._client: httpx.AsyncClient | None = None

    def _make_client(self) -> httpx.AsyncClient:
        base_url = os.getenv("K8S_API_URL")
        token_path = Path(os.getenv("K8S_TOKEN_FILE", str(TOKEN_PATH)))
        ca_path = Path(os.getenv("K8S_CA_FILE", str(CA_PATH)))

        if not base_url:
            host = os.getenv("KUBERNETES_SERVICE_HOST")
            port = os.getenv("KUBERNETES_SERVICE_PORT_HTTPS", "443")
            if not host:
                raise NamespaceApiUnavailable(
                    "set K8S_API_URL locally or run inside a Kubernetes pod"
                )
            base_url = f"https://{host}:{port}"

        headers: dict[str, str] = {}
        verify: bool | str = True
        if token_path.is_file():
            token = token_path.read_text(encoding="utf-8").strip()
            if token:
                headers["Authorization"] = f"Bearer {token}"
            if ca_path.is_file():
                verify = str(ca_path)

        return httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers=headers,
            verify=verify,
            timeout=8.0,
        )

    async def _refresh(self) -> None:
        if self._client is None:
            self._client = self._make_client()
        try:
            response = await self._client.get("/api/v1/namespaces")
            response.raise_for_status()
            payload = response.json()
            items = payload.get("items") if isinstance(payload, dict) else None
            if not isinstance(items, list):
                raise ValueError("Kubernetes API returned an invalid namespace list")

            labels_by_namespace: dict[str, dict[str, str]] = {}
            for item in items:
                if not isinstance(item, dict):
                    continue
                metadata = item.get("metadata") or {}
                name = metadata.get("name")
                labels = metadata.get("labels") or {}
                if name:
                    labels_by_namespace[str(name)] = {
                        str(key): str(value) for key, value in labels.items()
                    }

            self._labels = labels_by_namespace
            self._refreshed_at = time.monotonic()
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise NamespaceApiUnavailable("failed to refresh namespace metadata") from exc

    async def labels_for(self, namespace: str) -> dict[str, str] | None:
        """Return labels, or None when the namespace is not in the API list."""
        async with self._lock:
            expired = time.monotonic() - self._refreshed_at >= self.refresh_seconds
            if expired:
                await self._refresh()
            labels = self._labels.get(namespace)
            return dict(labels) if labels is not None else None

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


def should_filter_namespace(
    namespace: str,
    labels: Mapping[str, Any] | None,
    ignored_namespaces: set[str] | None = None,
) -> bool:
    """Default-allow policy: only explicit ignore config/label filters an alert."""
    if namespace in (ignored_namespaces or set()):
        return True
    return (labels or {}).get("security.falco.io/alerts", "").lower() == "disabled"
