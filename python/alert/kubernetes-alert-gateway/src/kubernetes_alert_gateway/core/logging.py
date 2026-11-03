import logging
import sys


def configure_logging() -> None:
    # Mọi logger có tên bắt đầu bằng "kubernetes_alert_gateway" sẽ dùng
    # cấu hình chung này, ví dụ logger của route Alertmanager.
    logger = logging.getLogger("kubernetes_alert_gateway")

    # Container và Kubernetes thu thập log từ stdout, vì vậy service không
    # cần tự ghi log vào file bên trong container.
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)

    # Uvicorn --reload có thể import module nhiều lần. Chỉ thêm handler khi
    # logger chưa có handler để tránh mỗi log bị in lặp lại.
    if not logger.handlers:
        logger.addHandler(handler)

    # INFO ghi lại cả hoạt động bình thường (sent, duplicate) lẫn lỗi.
    logger.setLevel(logging.INFO)

    # Không đẩy log lên root logger vì Uvicorn có handler riêng; làm vậy có
    # thể khiến cùng một bản ghi xuất hiện hai lần.
    logger.propagate = False
