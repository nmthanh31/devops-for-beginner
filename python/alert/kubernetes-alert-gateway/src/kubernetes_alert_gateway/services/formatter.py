from kubernetes_alert_gateway.domain.models import NormalizedAlert


def format_alert(alert: NormalizedAlert) -> str:
    # Đã sửa: tên hàm mô tả rõ nhiệm vụ định dạng một alert.
    alertname = alert.alert_name
    severity = alert.severity or "Không có"
    namespace = alert.namespace or "Không có namespace"

    # Đã sửa: thay placeholder Ellipsis bằng giá trị dự phòng dễ đọc.
    summary = (
        alert.summary
        or alert.description
        or "Không có mô tả"
    )
    if alert.status == "firing":
        status_emoji = "⚠️"
        status_text = "ĐANG CẢNH BÁO"
    else:
        # Đã sửa: alert đã hồi phục dùng icon khác với alert đang firing.
        status_emoji = "✅"
        status_text = "ĐÃ KHÔI PHỤC"

    # Đã sửa: message phải chứa trạng thái và các chi tiết, không chỉ severity.
    return (
        f"{status_emoji} [{status_text}] {alertname}\n"
        f"Severity: {severity}\n"
        f"Namespace: {namespace}\n"
        f"Details: {summary}"
    )
