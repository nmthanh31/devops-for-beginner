# 02. Cấu trúc dữ liệu

## List

`list` là tập hợp có thứ tự, có thể thay đổi và cho phép phần tử trùng nhau.

```python
numbers = [10, 20, 30]
numbers.append(40)
numbers[0] = 99
print(numbers[1:3])
```

Các phương thức thường dùng: `append`, `extend`, `insert`, `remove`, `pop`, `sort`, `reverse`.

## Tuple

`tuple` có thứ tự nhưng không thể thay đổi sau khi tạo. Dùng tuple cho nhóm giá trị cố định.

```python
point = (10, 20)
x, y = point
```

## Set

`set` lưu các phần tử duy nhất và hỗ trợ phép toán tập hợp.

```python
languages = {"Python", "Go", "Python"}
print(languages)
print({1, 2, 3} & {2, 3, 4})  # giao
print({1, 2, 3} | {2, 3, 4})  # hợp
```

## Dictionary

`dict` lưu dữ liệu theo cặp khóa-giá trị. Khóa phải có tính hashable, thường là chuỗi, số hoặc tuple bất biến.

```python
user = {"name": "Mai", "age": 28}
user["role"] = "developer"
print(user.get("email", "chưa cung cấp"))
```

Các phương thức hữu ích: `get`, `keys`, `values`, `items`, `update`, `pop`.

## Comprehension

Comprehension tạo cấu trúc dữ liệu ngắn gọn nhưng vẫn nên ưu tiên khả năng đọc.

```python
squares = [number ** 2 for number in range(5)]
even_squares = {number: number ** 2 for number in range(10) if number % 2 == 0}
```

## Chọn cấu trúc phù hợp

- Cần danh sách có thứ tự và thay đổi: `list`.
- Cần nhóm dữ liệu cố định: `tuple`.
- Cần loại trùng và kiểm tra thuộc nhanh: `set`.
- Cần ánh xạ khóa tới giá trị: `dict`.
