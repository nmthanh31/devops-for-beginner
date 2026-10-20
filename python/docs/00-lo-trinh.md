# 00. Lộ trình học Python

## Python là gì?

Python là ngôn ngữ lập trình thông dịch, cú pháp dễ đọc và có thư viện phong phú. Python được dùng cho tự động hóa, web, dữ liệu, kiểm thử, DevOps và trí tuệ nhân tạo.

## Mô hình thực thi

Mã nguồn Python thường được chạy bởi trình thông dịch:

```bash
python ten_file.py
```

Python biên dịch mã nguồn thành bytecode trước khi thực thi. Người học không cần quản lý bộ nhớ thủ công trong các chương trình thông thường vì Python có cơ chế garbage collection.

## Thứ tự học đề xuất

1. Biến, giá trị, toán tử và kiểu dữ liệu.
2. Điều kiện, vòng lặp và hàm.
3. List, tuple, set và dictionary.
4. Module, package và môi trường ảo.
5. Ngoại lệ, file và JSON.
6. Lập trình hướng đối tượng.
7. Kiểm thử, type hints và tổ chức dự án.

## Quy ước quan trọng

- Thụt lề bằng 4 dấu cách.
- Tên biến và hàm dùng `snake_case`.
- Tên lớp dùng `PascalCase`.
- Hằng số thường viết bằng `UPPER_CASE`.
- Một câu lệnh nên dễ đọc hơn là quá ngắn nhưng khó hiểu.

```python
student_name = "An"
MAX_RETRIES = 3

def print_greeting(name: str) -> None:
    print(f"Xin chào, {name}!")
```

## Cách đọc lỗi

Traceback thường cho biết:

1. Loại lỗi ở dòng cuối, ví dụ `TypeError`.
2. Thông báo giải thích lỗi.
3. Vị trí file và số dòng gây lỗi.

Hãy sửa nguyên nhân gốc thay vì chỉ che lỗi bằng `try/except` quá rộng.
