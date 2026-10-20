# 05. Ngoại lệ, file và JSON

## Ngoại lệ

Ngoại lệ biểu diễn tình huống chương trình không thể tiếp tục theo luồng bình thường.

```python
try:
    number = int(input("Nhập số: "))
except ValueError:
    print("Dữ liệu không phải số nguyên")
else:
    print(number * 2)
finally:
    print("Đã xử lý xong")
```

Chỉ bắt các loại lỗi có thể xử lý. Tránh `except Exception` nếu không có lý do rõ ràng.

## Tạo và ném ngoại lệ

```python
def withdraw(balance: float, amount: float) -> float:
    if amount < 0:
        raise ValueError("Số tiền phải không âm")
    if amount > balance:
        raise ValueError("Số dư không đủ")
    return balance - amount
```

## Đọc và ghi file

Luôn dùng `with` để file được đóng tự động:

```python
from pathlib import Path

path = Path("notes.txt")
path.write_text("Xin chào\n", encoding="utf-8")
content = path.read_text(encoding="utf-8")
```

Với file lớn, nên đọc từng dòng thay vì nạp toàn bộ vào bộ nhớ.

## JSON

JSON phù hợp để trao đổi dữ liệu dạng object, array, string, number, boolean và null.

```python
import json

data = {"name": "An", "skills": ["Python", "Linux"]}
text = json.dumps(data, ensure_ascii=False, indent=2)
loaded_data = json.loads(text)
```

Khi đọc JSON từ file, cần xử lý `json.JSONDecodeError` nếu dữ liệu có thể bị hỏng.

## CSV

Dùng module `csv` thay vì tự tách chuỗi bằng dấu phẩy, vì dữ liệu CSV có thể chứa dấu phẩy trong dấu ngoặc kép.

```python
import csv

with open("users.csv", newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        print(row["name"])
```
