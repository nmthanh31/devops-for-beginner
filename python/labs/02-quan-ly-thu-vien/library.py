import json
from datetime import date
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).with_name("books.json")
STATUS = ["Chưa đọc", "Đang đọc", "Đã đọc"]
# FIX: dict chỉ nhận 2 kiểu (kiểu khóa, kiểu giá trị), không nhận một kiểu cho mỗi field.
# Any được dùng tạm vì các field của sách có nhiều kiểu dữ liệu khác nhau.
Book = dict[str, Any]


def is_have_book_id(books: list[Book], book_id: str) -> bool:
    # FIX: kiểm tra trùng mã bằng cách duyệt từng sách; trả True ngay khi tìm thấy.
    for book in books:
        if book["id"] == book_id:
            return True
    return False


def make_book(book_id: str, name: str, author: str, year: int, status: str) -> Book:
    # FIX: dùng tên book_id thay cho id để tránh che khuất hàm dựng sẵn id().
    return {
        "id": book_id,
        "name": name,
        "author": author,
        "year": year,
        "status": status,
    }


def save_books(path: Path, books: list[Book]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False, indent=2)


def load_books(path: Path = DATA_FILE) -> list[Book]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []

    if not isinstance(data, list):
        raise ValueError("File JSON phải chứa danh sách sách.")
    # TODO: hiện mới kiểm tra JSON là list; chưa xác thực từng phần tử có đủ field và đúng kiểu.
    return data


def add_book_to_list(books: list[Book]) -> None:
    # FIX: bản trước chỉ hỏi nhập lại một lần, nên dữ liệu sai vẫn có thể lọt vào.
    # while giúp tiếp tục hỏi đến khi mã vừa có nội dung vừa không bị trùng.
    while True:
        book_id = input("Nhập mã sách: ").strip()
        if not book_id:
            print("Mã sách không được để trống.")
        elif is_have_book_id(books, book_id):
            print("Mã sách đã tồn tại, hãy nhập mã khác.")
        else:
            break

    # FIX: kiểm tra cả tên và tác giả, không chỉ kiểm tra rỗng một lần.
    name = input("Nhập tên sách: ").strip()
    while not name:
        print("Tên sách không được để trống.")
        name = input("Nhập tên sách: ").strip()

    author = input("Nhập tác giả: ").strip()
    while not author:
        print("Tên tác giả không được để trống.")
        author = input("Nhập tác giả: ").strip()

    # FIX: bắt ValueError nếu người dùng nhập chữ; năm cũng phải trong khoảng hợp lệ.
    current_year = date.today().year
    while True:
        try:
            year = int(input("Nhập năm xuất bản: "))
            if 1 <= year <= current_year:
                break
            print(f"Năm phải nằm trong khoảng 1 đến {current_year}.")
        except ValueError:
            print("Năm xuất bản phải là số nguyên.")

    # FIX: status: str in STATUS không phải cú pháp kiểm tra hợp lệ.
    # Kiểm tra membership trong thân hàm và lặp đến khi status thuộc STATUS.
    print("Trạng thái hợp lệ:", ", ".join(STATUS))
    status = input("Nhập trạng thái: ").strip()
    while status not in STATUS:
        print("Trạng thái không hợp lệ. Các lựa chọn:", ", ".join(STATUS))
        status = input("Nhập trạng thái: ").strip()

    books.append(make_book(book_id, name, author, year, status))
    print("Đã thêm sách.")


def list_books(books: list[Book]) -> None:
    if not books:
        print("Thư viện chưa có sách.")
        return

    # FIX: enumerate trả về (chỉ_số, phần_tử); không thể dùng for book, i in books.
    for i, book in enumerate(books, start=1):
        print(f"=== Sách {i} ===")
        print(f"Mã sách: {book['id']}")
        print(f"Tên sách: {book['name']}")
        print(f"Tác giả: {book['author']}")
        print(f"Năm xuất bản: {book['year']}")
        print(f"Trạng thái: {book['status']}")


def search(books: list[Book], query: str) -> list[Book]:
    # FIX: đổi tên tham số str vì str là tên kiểu dựng sẵn; chuẩn hóa cả hai vế để
    # tìm kiếm không phân biệt chữ hoa/chữ thường.
    query = query.strip().lower()
    return [
        book
        for book in books
        if query in book["name"].lower() or query in book["author"].lower()
    ]


def update_book(books: list[Book]) -> bool:
    # FIX: tìm sách theo mã rồi sửa trực tiếp dict của cuốn sách đó.
    # Bản trước duyệt list như thể mỗi phần tử gồm cả sách và chỉ số.
    book_id = input("Nhập mã sách cần cập nhật: ").strip()
    book = next((item for item in books if item["id"] == book_id), None)
    if book is None:
        print("Không tìm thấy mã sách.")
        return False

    print("Để trống nếu muốn giữ nguyên giá trị hiện tại.")
    name = input(f"Tên sách [{book['name']}]: ").strip()
    author = input(f"Tác giả [{book['author']}]: ").strip()
    if name:
        book["name"] = name
    if author:
        book["author"] = author

    current_year = date.today().year
    year_text = input(f"Năm xuất bản [{book['year']}]: ").strip()
    if year_text:
        while True:
            try:
                year = int(year_text)
                if 1 <= year <= current_year:
                    book["year"] = year
                    break
                print(f"Năm phải nằm trong khoảng 1 đến {current_year}.")
            except ValueError:
                print("Năm xuất bản phải là số nguyên.")
            year_text = input("Nhập lại năm xuất bản: ").strip()

    status = input(f"Trạng thái [{book['status']}]: ").strip()
    while status and status not in STATUS:
        print("Trạng thái không hợp lệ. Các lựa chọn:", ", ".join(STATUS))
        status = input("Nhập lại trạng thái (hoặc để trống để giữ nguyên): ").strip()
    if status:
        book["status"] = status

    print("Đã cập nhật sách.")
    return True


def delete_book(books: list[Book]) -> bool:
    # FIX: dùng del books[i]; remove là phương thức cần gọi bằng ngoặc, không dùng [] .
    book_id = input("Nhập mã sách cần xóa: ").strip()
    for i, book in enumerate(books):
        if book["id"] == book_id:
            confirm = input(f"Xóa sách '{book['name']}'? (c/k): ").strip().lower()
            if confirm == "c":
                del books[i]
                print("Đã xóa sách.")
                return True
            print("Đã hủy thao tác.")
            return False
    print("Không tìm thấy mã sách.")
    return False


def total_books(books: list[Book]) -> None:
    # FIX: len(books) lấy tổng số; count trước đây chỉ tham chiếu method, chưa gọi nó.
    # sum(1 ...) tăng bộ đếm đúng cách và thống kê đủ cả ba trạng thái.
    print(f"Tổng số sách: {len(books)}")
    for status in STATUS:
        count = sum(1 for book in books if book["status"] == status)
        print(f"{status}: {count}")


def main() -> None:
    books = load_books()
    while True:
        print("\n=== QUẢN LÝ SÁCH ===")
        print("1. Thêm sách mới")
        print("2. Hiển thị toàn bộ sách")
        print("3. Tìm sách theo tên hoặc tác giả")
        print("4. Cập nhật sách")
        print("5. Xóa sách")
        print("6. Xem thống kê")
        print("0. Thoát")

        # FIX: bỏ dấu backslash thừa gây nối dòng và phần menu còn tham chiếu expenses
        # của Lab 1; các nhánh bên dưới dùng books của Lab 2.
        choice = input("Bạn chọn: ").strip()
        if choice == "0":
            print("Hẹn gặp lại!")
            break
        elif choice == "1":
            # FIX: truyền books vào hàm và lưu ngay sau khi thêm thành công.
            add_book_to_list(books)
            save_books(DATA_FILE, books)
        elif choice == "2":
            if books.count == 0:
                print("Không có quyển sách nào")
            else:
                list_books(books)
        elif choice == "3":
            query = input("Nhập tên sách hoặc tác giả cần tìm: ")
            found_books = search(books, query)
            if found_books:
                list_books(found_books)
            else:
                print("Không tìm thấy sách phù hợp.")
        elif choice == "4":
            if update_book(books):
                save_books(DATA_FILE, books)
        elif choice == "5":
            if delete_book(books):
                save_books(DATA_FILE, books)
        elif choice == "6":
            total_books(books)
        else:
            print("Lựa chọn không hợp lệ. Hãy nhập từ 0 đến 6.")


if __name__ == "__main__":
    main()
