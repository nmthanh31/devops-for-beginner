"""HTTP entry point for Falcosidekick events."""

import json
import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, Request

from .formatter import format_message
from .namespace_api import NamespaceApiUnavailable, NamespaceCache, should_filter_namespace
from .rollout import WorkloadMonitor
from .telegram import TelegramDeliveryError, send_message


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
# HTTPX logs request URLs at INFO; Telegram Bot API URLs contain the bot token.
# Keep transport logs above INFO so credentials can never land in app logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("falco-router")

MAX_EVENT_BYTES = 1_048_576
namespace_cache = NamespaceCache()
workload_monitor = WorkloadMonitor(send_message)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await workload_monitor.close()
    await namespace_cache.close()


app = FastAPI(
    title="Falco Alert Formatter",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


async def _read_event(request: Request) -> dict:
    body = await request.body()
    if len(body) > MAX_EVENT_BYTES:
        raise HTTPException(status_code=413, detail="event body too large")

    try:
        event = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="invalid JSON event") from exc

    if not isinstance(event, dict):
        raise HTTPException(status_code=400, detail="event must be a JSON object")
    return event


def _format_and_log(event: dict) -> str:
    message = format_message(event)
    rule = str(event.get("rule") or "unknown")
    fields = event.get("output_fields")
    if not isinstance(fields, dict):
        fields = {}
    namespace = fields.get("ka.target.namespace") or fields.get("k8s.ns.name") or "unknown"
    logger.info("formatted Falco event rule=%s namespace=%s", rule, namespace)
    return message


def _namespace(event: dict) -> str | None:
    fields = event.get("output_fields")
    if not isinstance(fields, dict):
        return None
    return fields.get("ka.target.namespace") or fields.get("k8s.ns.name")


async def _namespace_policy(event: dict) -> bool:
    namespace = _namespace(event)
    if not namespace:
        return False  # cluster-scoped events are not filtered by namespace

    try:
        labels = await namespace_cache.labels_for(str(namespace))
    except NamespaceApiUnavailable as exc:
        logger.error("namespace lookup failed; event will be retried")
        raise HTTPException(status_code=503, detail="namespace lookup unavailable") from exc

    # An unknown namespace is allowed to avoid silently dropping an alert.
    ignored = {
        item.strip()
        for item in os.getenv("IGNORED_NAMESPACES", "").split(",")
        if item.strip()
    }
    return should_filter_namespace(str(namespace), labels, ignored)


@app.post("/falco/preview")
async def preview_event(request: Request) -> dict[str, str]:
    """Format an event without sending it; useful for local testing."""
    event = await _read_event(request)
    return {"status": "formatted", "message": _format_and_log(event)}


@app.post("/falco/events")
async def receive_event(request: Request) -> dict[str, str]:
    """Format and deliver one event to the configured Telegram chat."""
    event = await _read_event(request)
    try:
        filtered = await _namespace_policy(event)
    except HTTPException:
        raise
    if filtered:
        namespace = _namespace(event) or "unknown"
        logger.info("event filtered by namespace policy namespace=%s", namespace)
        return {"status": "filtered"}

    message = _format_and_log(event)
    try:
        await send_message(message)
    except TelegramDeliveryError as exc:
        logger.error("Telegram delivery failed: %s", exc)
        raise HTTPException(status_code=502, detail="Telegram delivery failed") from exc

    # Avoid logging or returning the bot token or full source event.
    logger.info("Telegram alert delivered")
    workload_monitor.track(event)
    return {"status": "sent"}
