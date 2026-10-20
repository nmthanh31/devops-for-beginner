# 07. Type hints, kiểm thử và quy tắc viết code

## Type hints

Type hints mô tả kiểu dữ liệu dự kiến, giúp IDE và công cụ kiểm tra phát hiện lỗi sớm. Python vẫn là ngôn ngữ động và không tự ép buộc type hints khi chạy.

```python
def average(numbers: list[float]) -> float:
    if not numbers:
        raise ValueError("Danh sách không được rỗng")
    return sum(numbers) / len(numbers)
```

Với giá trị có thể là `None`, dùng `str | None` trong Python hiện đại.

## Docstring

```python
def add_tax(price: float, rate: float) -> float:
    """Tính giá sau thuế theo tỷ lệ rate."""
    return price * (1 + rate)
```

## Kiểm thử với pytest

Một test nên kiểm tra một hành vi rõ ràng:

```python
from app.calculator import add_tax


def test_add_tax() -> None:
    assert add_tax(100, 0.1) == 110
```

Chạy test:

```bash
python -m pytest
```

## Các loại test

- Unit test: kiểm tra một hàm hoặc thành phần nhỏ.
- Integration test: kiểm tra nhiều thành phần kết hợp.
- End-to-end test: kiểm tra luồng gần với hành vi người dùng.

## Logging

Dùng `logging` thay vì nhiều lệnh `print` trong ứng dụng thực tế:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Ứng dụng đã khởi động")
```

## Quy tắc chất lượng

- Hàm ngắn, làm một việc rõ ràng.
- Tránh lặp code.
- Đặt tên mô tả ý định.
- Giữ dependency ở mức cần thiết.
- Format và lint code tự động trong CI nếu có thể.
