from datetime import UTC, datetime

import pytest

from kubernetes_alert_gateway.mappers.alertmanager import (
    map_alertmanager_payload,
)
from kubernetes_alert_gateway.schemas.alertmanager import (
    AlertItem,
    AlertmanagerPayload,
)


def create_payload(
    alerts: list[AlertItem],
    common_labels: dict[str, str] | None = None,
    common_annotations: dict[str, str] | None = None,
    external_url: str | None = None,
) -> AlertmanagerPayload:
    return AlertmanagerPayload(
        version="4",
        group_key="{}",
        status="firing",
        receiver="telegram",
        common_labels=common_labels or {},
        common_annotations=common_annotations or {},
        external_url=external_url,
        alerts=alerts,
    )


def test_maps_basic_alert():
    payload = create_payload(
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "alertname": "HighCPU",
                    "severity": "warning",
                    "cluster": "cluster-uat",
                    "namespace": "production",
                },
                annotations={
                    "summary": "CPU usage is high",
                    "description": "CPU has been above 90%",
                },
            )
        ]
    )

    result = map_alertmanager_payload(payload)

    assert len(result) == 1
    alert = result[0]
    assert alert.status == "firing"
    assert alert.source == "alertmanager"
    assert alert.alert_name == "HighCPU"
    assert alert.severity == "warning"
    assert alert.cluster == "cluster-uat"
    assert alert.namespace == "production"
    assert alert.summary == "CPU usage is high"
    assert alert.description == "CPU has been above 90%"
    assert len(alert.fingerprint) == 64


def test_merges_common_data_and_alert_data_takes_priority():
    payload = create_payload(
        common_labels={
            "cluster": "cluster-uat",
            "severity": "warning",
        },
        common_annotations={
            "summary": "Common summary",
            "description": "Common description",
        },
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "alertname": "HighCPU",
                    "severity": "critical",
                    "namespace": "production",
                },
                annotations={"summary": "Alert summary"},
            )
        ],
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.cluster == "cluster-uat"
    assert alert.severity == "critical"
    assert alert.summary == "Alert summary"
    assert alert.description == "Common description"
    assert alert.labels["namespace"] == "production"


@pytest.mark.parametrize(
    ("label_name", "label_value", "expected_kind"),
    [
        ("daemonset", "node-agent", "DaemonSet"),
        ("deployment", "frontend", "Deployment"),
        ("statefulset", "postgres", "StatefulSet"),
        ("cronjob", "backup", "CronJob"),
        ("job_name", "migration", "Job"),
        ("hpa", "frontend-hpa", "HPA"),
        ("horizontalpodautoscaler", "api-hpa", "HPA"),
        ("workload", "custom-workload", "Workload"),
    ],
)
def test_extracts_workload(
    label_name: str,
    label_value: str,
    expected_kind: str,
):
    payload = create_payload(
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "alertname": "WorkloadAlert",
                    label_name: label_value,
                },
            )
        ]
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.workload_kind == expected_kind
    assert alert.workload == label_value


def test_maps_resource_context():
    payload = create_payload(
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "alertname": "ResourceAlert",
                    "pod_name": "frontend-abc",
                    "container": "app",
                    "nodename": "worker-01",
                    "persistentvolumeclaim": "data-pvc",
                    "volume": "data",
                    "ingress": "frontend",
                    "service": "frontend-service",
                    "mountpoint": "/data",
                    "device": "/dev/sdb",
                },
            )
        ]
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.pod == "frontend-abc"
    assert alert.container == "app"
    assert alert.node == "worker-01"
    assert alert.pvc == "data-pvc"
    assert alert.volume == "data"
    assert alert.ingress == "frontend"
    assert alert.service == "frontend-service"
    assert alert.mountpoint == "/data"
    assert alert.device == "/dev/sdb"


def test_parses_dates_and_prefers_alert_generator_url():
    payload = create_payload(
        external_url="https://alertmanager.example.com",
        alerts=[
            AlertItem(
                status="resolved",
                starts_at="2026-10-28T10:00:00Z",
                ends_at="2026-10-28T10:05:00Z",
                generator_url="https://prometheus.example.com/graph",
            )
        ],
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.starts_at == datetime(
        2026,
        10,
        28,
        10,
        0,
        tzinfo=UTC,
    )
    assert alert.ends_at == datetime(
        2026,
        10,
        28,
        10,
        5,
        tzinfo=UTC,
    )
    assert alert.generator_url == "https://prometheus.example.com/graph"


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        "",
        "0001-01-01T00:00:00Z",
        "not-a-date",
    ],
)
def test_invalid_or_empty_dates_become_none(
    invalid_value: str | None,
):
    payload = create_payload(
        alerts=[
            AlertItem(
                status="firing",
                starts_at=invalid_value,
                ends_at=invalid_value,
            )
        ]
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.starts_at is None
    assert alert.ends_at is None


def test_uses_external_url_when_alert_has_no_generator_url():
    payload = create_payload(
        external_url="https://alertmanager.example.com",
        alerts=[AlertItem(status="firing")],
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.generator_url == "https://alertmanager.example.com"


def test_empty_alert_list_returns_empty_list():
    payload = create_payload(alerts=[])

    assert map_alertmanager_payload(payload) == []


def test_missing_alert_name_uses_fallback():
    payload = create_payload(
        alerts=[AlertItem(status="firing")],
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.alert_name == "UnnamedAlert"


def test_fingerprint_is_stable_when_label_order_changes():
    first_payload = create_payload(
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "alertname": "HighCPU",
                    "namespace": "production",
                },
            )
        ]
    )
    second_payload = create_payload(
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "namespace": "production",
                    "alertname": "HighCPU",
                },
            )
        ]
    )

    first = map_alertmanager_payload(first_payload)[0]
    second = map_alertmanager_payload(second_payload)[0]

    assert first.fingerprint == second.fingerprint


def test_filters_monitoring_scraper_metadata():
    payload = create_payload(
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "alertname": "KubeDaemonSetNotScheduled",
                    "namespace": "monitoring",
                    "daemonset": "node-agent",
                    "pod": "rancher-monitoring-kube-state-metrics-abc",
                    "container": "kube-state-metrics",
                    "instance": "10.0.0.10:8080",
                    "job": "kube-state-metrics",
                    "service": "rancher-monitoring-kube-state-metrics",
                },
            )
        ]
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.workload_kind == "DaemonSet"
    assert alert.workload == "node-agent"
    assert alert.pod is None
    assert alert.container is None
    assert alert.instance is None
    assert alert.job is None
    assert alert.service is None


def test_target_down_preserves_target_metadata():
    payload = create_payload(
        alerts=[
            AlertItem(
                status="firing",
                labels={
                    "alertname": "TargetDown",
                    "job": "node-exporter",
                    "service": "rancher-monitoring-node-exporter",
                    "instance": "10.0.0.20:9100",
                },
            )
        ]
    )

    alert = map_alertmanager_payload(payload)[0]

    assert alert.job == "node-exporter"
    assert alert.service == "rancher-monitoring-node-exporter"
    assert alert.instance == "10.0.0.20:9100"
