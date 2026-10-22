# Lab Python tổng hợp — Quản lý chi tiêu cá nhân

Lab này độc lập với Kubernetes/Falco. Giả sử bạn đang bắt đầu lại từ đầu sau một thời gian không viết code. Hãy làm tuần tự; không cần hiểu hết cả bài ngay lần đầu.

## Sản phẩm cuối

Viết chương trình chạy trong terminal để:

1. thêm một khoản chi;
2. xem danh sách khoản chi;
3. xem tổng tiền và tổng theo từng danh mục;
4. lưu dữ liệu vào file JSON để lần chạy sau vẫn còn;
5. báo lỗi thân thiện khi người dùng nhập sai.

Ví dụ một khoản chi lưu trong Python:

```python
{
    "amount": 45000.0,
    "category": "Ăn uống",
    "note": "Bữa trưa",
}
```

## Chuẩn bị và cách chạy

Mở Git Bash tại thư mục dự án:

```bash
cd /d/Documents/F/python/labs/01-quan-ly-chi-tieu
python --version
```

Chạy ví dụ đầu tiên:

```bash
python bai_01_khoi_dong.py
```

`expense_tracker.py` là bộ khung đang có TODO. Chương trình hoàn chỉnh sẽ chạy được sau khi làm các phần 7–10.

Chạy kiểm thử (sau khi hoàn thành các hàm và lưu/đọc JSON ở phần 7–9):

```bash
python -m unittest discover -s tests -v
```

Không cần cài thư viện ngoài; lab chỉ dùng thư viện có sẵn của Python.

---

## Phần 1 — Chạy một chương trình Python

Python chạy các lệnh từ trên xuống dưới. Ví dụ:

```python
print("Xin chào!")
print(2 + 3)
```

`print()` hiển thị dữ liệu ra terminal. Trong file `expense_tracker.py`, hàm `main()` là điểm bắt đầu chương trình.

Thử sửa dòng lời chào trong `main()`, chạy file, rồi sửa lại nếu cần.

## Phần 2 — Biến và kiểu dữ liệu

Biến là tên mình đặt cho một giá trị:

```python
amount = 45000.0       # float: số có phần thập phân
category = "Ăn uống"  # str: chuỗi ký tự
is_valid = True        # bool: đúng hoặc sai
```

Một số kiểu cơ bản:

| Kiểu | Ví dụ | Dùng để |
|---|---|---|
| `str` | `"Ăn uống"` | văn bản |
| `int` | `3` | số nguyên |
| `float` | `45000.0` | số thập phân, tiền |
| `bool` | `True`, `False` | trạng thái đúng/sai |
| `None` | `None` | chưa có giá trị |

`input()` luôn trả về chuỗi, kể cả khi bạn gõ số:

```python
raw_amount = input("Số tiền: ")
print(type(raw_amount))  # <class 'str'>
```

Đổi chuỗi số sang số thực bằng `float()`:

```python
amount = float(raw_amount)
```

## Phần 3 — Chuỗi và f-string

F-string giúp ghép biến vào câu dễ đọc:

```python
category = "Ăn uống"
amount = 45000
print(f"Danh mục {category}: {amount:,.0f} đồng")
```

**Thử:** in câu `Bạn đã chi 45000 đồng cho Ăn uống` bằng f-string.

## Phần 4 — Điều kiện `if / elif / else`

Điều kiện cho chương trình chọn nhánh cần chạy:

```python
amount = 45000

if amount <= 0:
    print("Số tiền phải lớn hơn 0")
elif amount < 100000:
    print("Khoản chi nhỏ")
else:
    print("Khoản chi lớn")
```

Lưu ý: Python dùng dấu `:` sau điều kiện và thụt lề cho phần code bên trong.

**Thử:** trong `main()`, nếu menu người dùng nhập là `1` thì in `Thêm khoản chi`; nếu là `2` thì in `Xem các khoản chi`; các giá trị khác in `Lựa chọn không hợp lệ`.

## Phần 5 — List và dictionary

List lưu nhiều phần tử theo thứ tự:

```python
categories = ["Ăn uống", "Di chuyển", "Khác"]
print(categories[0])  # Ăn uống; chỉ số bắt đầu từ 0
```

Dictionary lưu dữ liệu theo cặp khóa/giá trị:

```python
expense = {"amount": 45000.0, "category": "Ăn uống", "note": "Bữa trưa"}
print(expense["category"])
```

Danh sách chi tiêu sẽ là list chứa nhiều dictionary:

```python
expenses = [
    {"amount": 45000.0, "category": "Ăn uống", "note": "Bữa trưa"},
    {"amount": 20000.0, "category": "Di chuyển", "note": "Gửi xe"},
]
```

Lấy phần tử đầu tiên: `expenses[0]`. Lấy ghi chú của nó: `expenses[0]["note"]`.

## Phần 6 — Vòng lặp

Dùng `for` để duyệt toàn bộ khoản chi:

```python
for expense in expenses:
    print(expense["category"], expense["amount"])
```

Dùng `while` để lặp menu đến khi người dùng chọn thoát:

```python
while True:
    choice = input("Chọn chức năng: ")
    if choice == "0":
        break
```

`break` thoát khỏi vòng lặp gần nhất. Trong menu lab, lựa chọn `0` sẽ kết thúc chương trình.

## Phần 7 — Hàm

Hàm gom một nhiệm vụ thành khối có tên, để gọi lại nhiều lần:

```python
def total_expenses(expenses):
    total = 0
    for expense in expenses:
        total += expense["amount"]
    return total
```

- `def` bắt đầu khai báo hàm.
- `expenses` là tham số đầu vào.
- `return` trả kết quả về nơi gọi hàm.

Trong `expense_tracker.py`, hoàn thành các hàm theo thứ tự:

1. `parse_amount(raw)`: đổi chuỗi thành `float`; từ chối chữ, số 0 và số âm bằng `ValueError`.
2. `make_expense(amount, category, note)`: tạo và trả về một dictionary khoản chi.
3. `total_expenses(expenses)`: trả về tổng tiền.
4. `totals_by_category(expenses)`: trả về dictionary tổng tiền theo danh mục.

Ví dụ `totals_by_category()` với dữ liệu mẫu cần trả:

```python
{"Ăn uống": 45000.0, "Di chuyển": 20000.0}
```

## Phần 8 — Xử lý lỗi

Người dùng có thể nhập `abc` thay vì số. `float("abc")` gây `ValueError`. Bắt lỗi để chương trình không bị dừng đột ngột:

```python
try:
    amount = float(raw_amount)
except ValueError:
    print("Vui lòng nhập số, ví dụ 45000")
```

Trong `parse_amount()`, hãy bắt lỗi đổi số và ném lại `ValueError` với lời nhắc dễ hiểu. Sau đó trong menu, bắt `ValueError` và cho người dùng nhập lại.

Không nên dùng `except:` trống: nó bắt mọi loại lỗi, kể cả lỗi lập trình mà ta cần nhìn thấy.

## Phần 9 — Lưu và đọc JSON

JSON là định dạng văn bản phổ biến để lưu list/dictionary. Python có module `json` tích hợp sẵn:

```python
import json

with open("expenses.json", "w", encoding="utf-8") as file:
    json.dump(expenses, file, ensure_ascii=False, indent=2)
```

- `"w"` mở để ghi; `"r"` mở để đọc.
- `with` tự đóng file sau khi hoàn tất.
- `ensure_ascii=False` giữ tiếng Việt dễ đọc.
- `indent=2` thụt lề để file dễ xem.

Hoàn thành `save_expenses(path, expenses)` và `load_expenses(path)` trong file. Khi file chưa tồn tại, `load_expenses()` nên trả về `[]`. Bắt riêng `FileNotFoundError`; đừng để việc chạy lần đầu làm chương trình lỗi.

## Phần 10 — Ghép thành ứng dụng menu

Hoàn thiện `main()` để có menu:

```text
=== QUẢN LÝ CHI TIÊU ===
1. Thêm khoản chi
2. Xem khoản chi
3. Xem tổng theo danh mục
0. Lưu và thoát
```

Yêu cầu:

- Khi thêm: hỏi số tiền, danh mục, ghi chú; kiểm tra số tiền hợp lệ; thêm dictionary mới vào list.
- Khi xem: dùng `for` để in từng khoản; nếu list rỗng, báo chưa có dữ liệu.
- Khi tổng kết: gọi `total_expenses()` và `totals_by_category()`.
- Khi thoát: lưu JSON rồi kết thúc vòng `while`.
- Lựa chọn không hợp lệ không được làm chương trình dừng.

Gợi ý thêm phần tử vào list:

```python
expenses.append(make_expense(amount, category, note))
```

## Phần 11 — Module và điểm bắt đầu

`import json` nghĩa là dùng module `json` của thư viện chuẩn. File Python của bạn cũng là một module.

Đoạn dưới đây chỉ gọi `main()` khi chạy trực tiếp file, không gọi khi file được import để test:

```python
if __name__ == "__main__":
    main()
```

Trong lab đầu tiên, giữ mọi hàm trong `expense_tracker.py` để đỡ phải quản lý nhiều file. Sau khi chạy được, thử tách các hàm xử lý dữ liệu sang `storage.py` và import chúng lại.

## Phần 12 — Kiểm thử tự động

Thư mục `tests/` có các bài test cho hàm xử lý tiền, tổng hợp và JSON. Chạy:

```bash
python -m unittest discover -s tests -v
```

Mỗi dòng `... ok` nghĩa là một hành vi đúng. Nếu test báo lỗi, đọc tên test và dòng cuối của thông báo trước; thường test đang cho biết đầu vào và kết quả mong đợi.

## Checklist hoàn thành

- [x] Chạy được menu và thoát bằng `0`.
- [x] Thêm được nhiều khoản chi trong một lần chạy.
- [x] Từ chối số tiền sai, bằng 0 hoặc âm mà không làm app crash.
- [x] Hiển thị tổng tất cả khoản và tổng từng danh mục.
- [ ] Dữ liệu vẫn còn sau khi tắt rồi chạy lại chương trình.
- [ ] Các test đều báo `ok`.

## Thử thách thêm (chỉ làm sau khi checklist hoàn tất)

1. Thêm ngày chi tiêu bằng `datetime.date.today().isoformat()`.
2. Cho phép lọc danh sách theo danh mục.
3. Thêm chức năng xóa khoản chi theo số thứ tự.
4. Không cho danh mục chỉ chứa khoảng trắng.
5. Thêm kiểm thử cho trường hợp file JSON hỏng.
