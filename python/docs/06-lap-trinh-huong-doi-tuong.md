# 06. Lập trình hướng đối tượng

## Khái niệm

- Class là bản thiết kế.
- Object là một thể hiện của class.
- Attribute là dữ liệu của object.
- Method là hành vi của object.

```python
class BankAccount:
    def __init__(self, owner: str, balance: float = 0) -> None:
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        self.balance += amount

account = BankAccount("An")
account.deposit(100)
```

## Encapsulation

Python không có private tuyệt đối như một số ngôn ngữ. Tên bắt đầu bằng `_` là quy ước nội bộ; tên bắt đầu bằng `__` kích hoạt name mangling.

## Property

`property` cho phép kiểm soát việc đọc và ghi attribute:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Nhiệt độ thấp hơn độ không tuyệt đối")
        self._celsius = value
```

## Kế thừa và composition

Kế thừa biểu diễn quan hệ “là một”, còn composition biểu diễn quan hệ “có một”. Ưu tiên composition khi nó giúp các thành phần ít phụ thuộc nhau hơn.

## Dataclass

`dataclass` giảm mã lặp cho các class chủ yếu dùng để lưu dữ liệu:

```python
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
```

Không cần dùng class cho mọi bài toán. Hàm và cấu trúc dữ liệu đơn giản thường rõ ràng hơn.
