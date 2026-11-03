import re
from datetime import datetime

from kubernetes_alert_gateway.domain.models import NormalizedAlert
from kubernetes_alert_gateway.schemas.alertmanager import (
    AlertItem,
    AlertmanagerPayload,
)
from kubernetes_alert_gateway.services.fingerprint import (
    generate_alert_fingerprint,
)

_SCRAPER_POD_PATTERN = re.compile(
    r"^(rancher-monitoring-)?"
    r"(kube-state-metrics|node-exporter|prometheus|alertmanager)-",
    re.IGNORECASE,
)

_INTERNAL_SCRAPE_JOBS = {
    "kube-state-metrics",
    "node-exporter",
    "kubelet",
    "cAdvisor",
    "prometheus-k8s",
    "apiserver",
}


def _parse_datetime(value: str | None) -> datetime | None:
    """Chuyển thời gian ISO của Alertmanager thành datetime an toàn."""

    if not value or value.startswith("0001-01-01"):
        return None

    normalized_value = (
        value[:-1] + "+00:00"
        if value.endswith("Z")
        else value
    )

    try:
        return datetime.fromisoformat(normalized_value)
    except ValueError:
        return None


def _extract_workload(
    labels: dict[str, str],
) -> tuple[str | None, str | None]:
    """Trả về loại workload và tên workload theo thứ tự ưu tiên."""

    workload_labels = (
        ("daemonset", "DaemonSet"),
        ("deployment", "Deployment"),
        ("statefulset", "StatefulSet"),
        ("cronjob", "CronJob"),
        ("job_name", "Job"),
        ("hpa", "HPA"),
        ("horizontalpodautoscaler", "HPA"),
        ("workload", "Workload"),
    )

    for label_name, workload_kind in workload_labels:
        workload_name = labels.get(label_name)
        if workload_name:
            return workload_kind, workload_name

    return None, None


def map_alert_item(
    alert: AlertItem,
    payload: AlertmanagerPayload,
) -> NormalizedAlert:
    """Chuẩn hóa một alert từ Alertmanager thành model nội bộ."""

    # Dictionary đứng sau ghi đè dictionary đứng trước. Nhờ đó dữ liệu riêng
    # của alert luôn được ưu tiên hơn common data của nhóm alert.
    merged_labels = {
        **payload.common_labels,
        **alert.labels,
    }
    merged_annotations = {
        **payload.common_annotations,
        **alert.annotations,
    }

    alert_name = (
        merged_labels.get("alertname")
        or merged_labels.get("alert_name")
        or "UnnamedAlert"
    )
    severity = (
        merged_labels.get("severity")
        or merged_labels.get("priority")
    )
    cluster = (
        merged_labels.get("cluster")
        or merged_labels.get("cluster_name")
    )
    namespace = (
        merged_labels.get("namespace")
        or merged_labels.get("kubernetes_namespace")
    )

    workload_kind, workload = _extract_workload(merged_labels)

    pvc = (
        merged_labels.get("persistentvolumeclaim")
        or merged_labels.get("pvc")
    )
    volume = merged_labels.get("volume")
    node = merged_labels.get("node") or merged_labels.get("nodename")
    ingress = merged_labels.get("ingress")

    raw_job = merged_labels.get("job", "")
    raw_pod = (
        merged_labels.get("pod")
        or merged_labels.get("pod_name")
        or ""
    )
    raw_container = merged_labels.get("container", "")
    raw_service = merged_labels.get("service", "")

    is_kube_state_metrics_scrape = (
        raw_job == "kube-state-metrics"
        or "kube-state-metrics" in raw_service
        or raw_container == "kube-state-metrics"
    )
    is_node_exporter_scrape = (
        raw_job == "node-exporter"
        or "node-exporter" in raw_service
        or raw_container == "node-exporter"
    )
    has_resource_context = any(
        (workload, pvc, node, ingress)
    )
    is_exporter_pod = has_resource_context and (
        is_kube_state_metrics_scrape
        or is_node_exporter_scrape
        or _SCRAPER_POD_PATTERN.match(raw_pod) is not None
    )

    pod = raw_pod if raw_pod and not is_exporter_pod else None

    is_exporter_container = (
        bool(workload or pvc or node or ingress) or not pod
    ) and raw_container in {
        "kube-state-metrics",
        "node-exporter",
        "prometheus",
    }
    container = (
        raw_container
        if raw_container and not is_exporter_container
        else None
    )

    raw_instance = merged_labels.get("instance")
    is_scraper_instance = (
        is_kube_state_metrics_scrape
        and bool(workload or pod or pvc or node or ingress or namespace)
    )
    instance = (
        raw_instance
        if raw_instance
        and not is_scraper_instance
        and raw_instance != node
        else None
    )

    is_internal_scrape_job = (
        raw_job in _INTERNAL_SCRAPE_JOBS
        or raw_job.startswith("rancher-monitoring-")
    )
    job = (
        raw_job
        if raw_job
        and (
            not is_internal_scrape_job
            or alert_name == "TargetDown"
        )
        else None
    )

    is_scraper_service = (
        "kube-state-metrics" in raw_service
        or "node-exporter" in raw_service
        or "prometheus" in raw_service
        or "alertmanager" in raw_service
        or raw_service.startswith("rancher-monitoring-")
    )
    service = (
        raw_service
        if raw_service
        and (
            not is_scraper_service
            or alert_name == "TargetDown"
        )
        else None
    )

    summary = (
        merged_annotations.get("summary")
        or merged_annotations.get("message")
    )
    description = (
        merged_annotations.get("description")
        or merged_annotations.get("info")
    )
    starts_at = _parse_datetime(alert.starts_at)
    ends_at = _parse_datetime(alert.ends_at)
    generator_url = alert.generator_url or payload.external_url
    fingerprint = generate_alert_fingerprint(
        labels=merged_labels,
        status=alert.status,
        starts_at=alert.starts_at,
    )

    return NormalizedAlert(
        status=alert.status,
        source="alertmanager",
        alert_name=alert_name,
        severity=severity,
        fingerprint=fingerprint,
        cluster=cluster,
        namespace=namespace,
        workload=workload,
        workload_kind=workload_kind,
        pod=pod,
        container=container,
        node=node,
        instance=instance,
        job=job,
        pvc=pvc,
        volume=volume,
        ingress=ingress,
        service=service,
        mountpoint=merged_labels.get("mountpoint"),
        device=merged_labels.get("device"),
        summary=summary,
        description=description,
        starts_at=starts_at,
        ends_at=ends_at,
        generator_url=generator_url,
        labels=merged_labels,
        annotations=merged_annotations,
    )


def map_alertmanager_payload(
    payload: AlertmanagerPayload,
) -> list[NormalizedAlert]:
    """Chuẩn hóa toàn bộ alerts trong một webhook Alertmanager."""

    return [
        map_alert_item(alert=alert, payload=payload)
        for alert in payload.alerts
    ]
