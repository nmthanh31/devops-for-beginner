# 03. Điều kiện, vòng lặp và hàm

## Điều kiện

```python
score = 8.5

if score >= 8:
    result = "Tốt"
elif score >= 5:
    result = "Đạt"
else:
    result = "Chưa đạt"
```

Python dùng thụt lề để xác định khối lệnh. Không trộn tab và dấu cách.

## Vòng lặp `for`

```python
for index, name in enumerate(["An", "Bình"]):
    print(index, name)
```

`range(start, stop, step)` tạo dãy số, trong đó `stop` không được bao gồm.

## Vòng lặp `while`

```python
attempt = 0
while attempt < 3:
    print("Thử lần", attempt + 1)
    attempt += 1
```

`break` kết thúc vòng lặp; `continue` bỏ qua phần còn lại của lượt hiện tại.

## Hàm

Hàm giúp gom logic, tái sử dụng và kiểm thử dễ hơn.

```python
def calculate_total(price: float, quantity: int = 1) -> float:
    return price * quantity

total = calculate_total(25.5, quantity=2)
```

Tham số mặc định nên dùng giá trị bất biến. Không dùng `[]` hoặc `{}` làm giá trị mặc định.

## Phạm vi biến

Biến cục bộ tồn tại trong hàm. Hạn chế dùng `global`; nên truyền dữ liệu qua tham số và trả về kết quả.

## `*args` và `**kwargs`

```python
def summarize(*numbers: int, **metadata: str) -> None:
    print(sum(numbers), metadata)

summarize(1, 2, 3, source="test")
```

## Lambda và hàm bậc cao

Lambda phù hợp với biểu thức ngắn, ví dụ khi dùng `sorted`:

```python
users = [{"name": "An", "age": 30}, {"name": "Bình", "age": 20}]
users.sort(key=lambda user: user["age"])
```

Không nên dùng lambda cho logic nhiều dòng hoặc khó đọc.
