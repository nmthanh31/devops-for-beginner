from kubernetes_alert_gateway.domain.models import NormalizedAlert
from kubernetes_alert_gateway.services.formatter import format_alert


def test_format_firing_alert():
    alert = NormalizedAlert(
        status="firing",
        source="alertmanager",
        alert_name="HighCPU",
        severity="warning",
        fingerprint="test-fingerprint",
        namespace="production",
        summary="CPU usage is high",
    )

    message = format_alert(alert)
    assert "[ĐANG CẢNH BÁO]" in message
    assert "HighCPU" in message
    assert "warning" in message
    assert "production" in message
    assert "CPU usage is high" in message


def test_format_resolved_alert():
    alert = NormalizedAlert(
        status="resolved",
        source="alertmanager",
        alert_name="HighCPU",
        severity="warning",
        fingerprint="test-fingerprint",
        namespace="production",
        summary="CPU usage is high",
    )

    message = format_alert(alert)
    assert "✅ [ĐÃ KHÔI PHỤC]" in message
    assert "[ĐÃ KHÔI PHỤC]" in message
    assert "HighCPU" in message
    assert "warning" in message
    assert "production" in message
    assert "CPU usage is high" in message


def test_missing_optional_fields_use_fallbacks():
    alert = NormalizedAlert(
        status="firing",
        source="alertmanager",
        alert_name="UnnamedAlert",
        fingerprint="test-fingerprint",
    )

    message = format_alert(alert)

    assert "UnnamedAlert" in message
    assert "Không có" in message
    assert "Không có namespace" in message
    assert "Không có mô tả" in message


# def test_missing_labels_annotations():
#     # Đã sửa: kiểm tra formatter có fallback khi hai field tùy chọn bị thiếu.
#     alert = NormalizedAlert(
#         status="firing",
#         source="alertmanager",
#         alert_name="",
#         fingerprint="",
#     )

#     message = format_alert(alert)

#     assert "Không có tên" in message
#     assert "Không rõ" in message
#     assert "Không có namespace" in message
#     assert "Không có mô tả" in message
