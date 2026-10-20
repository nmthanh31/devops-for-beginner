# 08. Kiến thức Python thực tế

## Iterator và generator

Iterator cung cấp từng phần tử theo thứ tự. Generator tạo giá trị khi cần, giúp tiết kiệm bộ nhớ:

```python
def read_numbers(limit: int):
    for number in range(limit):
        yield number

for number in read_numbers(3):
    print(number)
```

## Context manager

Context manager quản lý tài nguyên theo cặp mở-đóng, thường dùng qua `with`.

File là ví dụ phổ biến. Có thể tự tạo context manager bằng class hoặc `contextlib.contextmanager`.

## Decorator

Decorator bọc một hàm để thêm hành vi mà không sửa thân hàm gốc.

```python
from functools import wraps

def announce(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Bắt đầu")
        result = func(*args, **kwargs)
        print("Kết thúc")
        return result
    return wrapper
```

## Async và await

`asyncio` phù hợp với nhiều tác vụ chờ I/O như gọi mạng hoặc đọc dịch vụ. Nó không tự làm cho tác vụ CPU nặng chạy nhanh hơn.

```python
import asyncio

async def main() -> None:
    await asyncio.sleep(1)
    print("Hoàn thành")

asyncio.run(main())
```

## Hiệu năng

- Đo trước khi tối ưu bằng `timeit` hoặc profiler.
- Chọn cấu trúc dữ liệu phù hợp.
- Tránh đọc toàn bộ file lớn vào bộ nhớ nếu không cần.
- Dùng thư viện chuẩn hoặc dependency uy tín.

## An toàn

- Không dùng `eval()` với dữ liệu người dùng.
- Không chạy shell command từ input chưa kiểm soát.
- Không ghi mật khẩu, token và khóa API vào source code.
- Kiểm tra dữ liệu đầu vào và giới hạn quyền của chương trình.

## Checklist trước khi hoàn thành project

- Có README hướng dẫn chạy.
- Dependency được khai báo rõ.
- Có test cho logic quan trọng.
- Có xử lý lỗi phù hợp.
- Có logging đủ để chẩn đoán.
- Không commit secret hoặc file môi trường cá nhân.
