from kubernetes_alert_gateway.services.fingerprint import (
    generate_alert_fingerprint,
)


def test_label_order_does_not_change_fingerprint():
    labels_one = {
        "alertname": "HighCPU",
        "namespace": "production",
    }
    labels_two = {
        "namespace": "production",
        "alertname": "HighCPU",
    }

    fingerprint_one = generate_alert_fingerprint(
        labels=labels_one,
        status="firing",
        starts_at="2026-10-28T10:00:00Z",
    )
    fingerprint_two = generate_alert_fingerprint(
        labels=labels_two,
        status="firing",
        starts_at="2026-10-28T10:00:00Z",
    )

    assert fingerprint_one == fingerprint_two


def test_different_status_produces_different_fingerprint():
    labels = {"alertname": "HighCPU"}

    firing = generate_alert_fingerprint(
        labels=labels,
        status="firing",
    )
    resolved = generate_alert_fingerprint(
        labels=labels,
        status="resolved",
    )

    assert firing != resolved


def test_different_start_time_produces_different_fingerprint():
    labels = {"alertname": "HighCPU"}

    first = generate_alert_fingerprint(
        labels=labels,
        status="firing",
        starts_at="2026-10-28T10:00:00Z",
    )
    second = generate_alert_fingerprint(
        labels=labels,
        status="firing",
        starts_at="2026-10-28T11:00:00Z",
    )

    assert first != second


def test_empty_labels_produces_valid_fingerprint():
    result = generate_alert_fingerprint(
        labels={},
        status="firing",
    )

    assert isinstance(result, str)
    assert len(result) == 64


def test_status_is_case_insensitive():
    labels = {"alertname": "HighCPU"}

    lowercase = generate_alert_fingerprint(
        labels=labels,
        status="firing",
    )
    uppercase = generate_alert_fingerprint(
        labels=labels,
        status="FIRING",
    )

    assert lowercase == uppercase
