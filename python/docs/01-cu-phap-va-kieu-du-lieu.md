# 01. Cú pháp và kiểu dữ liệu cơ bản

## Biến và phép gán

Python không yêu cầu khai báo kiểu biến trước. Biến là tên tham chiếu tới một đối tượng.

```python
age = 25
name = "Lan"
is_active = True
```

Phép gán nhiều biến:

```python
width, height = 10, 5
width, height = height, width
```

## Kiểu dữ liệu chính

| Kiểu | Ví dụ | Ý nghĩa |
|---|---|---|
| `int` | `42` | số nguyên |
| `float` | `3.14` | số thực |
| `complex` | `2 + 3j` | số phức |
| `bool` | `True` | đúng hoặc sai |
| `str` | `"Python"` | chuỗi ký tự |
| `None` | `None` | không có giá trị |

Kiểm tra kiểu bằng `type()` hoặc kiểm tra tương thích bằng `isinstance()`:

```python
value = 42
print(type(value))
print(isinstance(value, int))
```

## Chuỗi

Chuỗi là bất biến, tức là không thể sửa một ký tự trực tiếp trong chuỗi đã tạo.

```python
first_name = "Nguyen"
last_name = "An"
full_name = f"{first_name} {last_name}"
print(full_name.upper())
print(full_name.lower())
```

Các thao tác thường dùng: `strip()`, `split()`, `join()`, `replace()`, `startswith()`, `endswith()`.

## Toán tử

- Số học: `+`, `-`, `*`, `/`, `//`, `%`, `**`.
- So sánh: `==`, `!=`, `<`, `<=`, `>`, `>=`.
- Logic: `and`, `or`, `not`.
- Kiểm tra thuộc: `in`, `not in`.
- Kiểm tra cùng đối tượng: `is`, `is not`.

Không dùng `is` để so sánh giá trị thông thường; hãy dùng `==`.

## Nhập và xuất dữ liệu

`input()` luôn trả về chuỗi, vì vậy cần chuyển kiểu khi cần:

```python
age = int(input("Tuổi của bạn: "))
print(f"Năm sau bạn {age + 1} tuổi.")
```

## Giá trị đúng và sai

Các giá trị rỗng như `None`, `False`, `0`, `0.0`, `""`, `[]` và `{}` được xem là false trong điều kiện.
