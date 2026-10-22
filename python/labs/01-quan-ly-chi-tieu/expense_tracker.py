"""Lab tổng hợp Python: ứng dụng quản lý chi tiêu cá nhân."""

import json
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).with_name("expenses.json")


def parse_amount(raw: str) -> float:
    """Đổi chuỗi nhập thành số tiền dương; TODO: hoàn thiện theo README."""
    # raise NotImplementedError("Hãy hoàn thiện parse_amount() ở Phần 7 và 8")
    try:
        amount = float(raw)
    except ValueError as error:
        raise ValueError("Vui lòng nhập số hợp lệ, ví dụ 45000") from error

    if amount <= 0:
        raise ValueError("Số tiền phải lớn hơn 0")

    return amount


def make_expense(amount: float, category: str, note: str) -> dict[str, Any]:
    """Tạo dictionary cho một khoản chi; TODO: hoàn thiện theo README."""
    # raise NotImplementedError("Hãy hoàn thiện make_expense() ở Phần 7")
    return {"amount": amount, "category": category, "note": note}


def total_expenses(expenses: list[dict[str, Any]]) -> float:
    """Tính tổng chi tiêu; TODO: hoàn thiện theo README."""
    # raise NotImplementedError("Hãy hoàn thiện total_expenses() ở Phần 7")
    total = 0
    for expense in expenses:
        total += expense["amount"]
    return total


def totals_by_category(expenses: list[dict[str, Any]]) -> dict[str, float]:
    """Tính tổng tiền theo danh mục; TODO: hoàn thiện theo README."""
    # raise NotImplementedError("Hãy hoàn thiện totals_by_category() ở Phần 7")
    totals = {}
    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]

        if category not in totals:
            totals[category] = 0.0

        totals[category] += amount
    return totals
        


def load_expenses(path: Path = DATA_FILE) -> list[dict[str, Any]]:
    """Đọc JSON; nếu file chưa có, trả về list rỗng."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_expenses(path: Path, expenses: list[dict[str, Any]]) -> None:
    """Lưu danh sách khoản chi xuống JSON."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(expenses, file, ensure_ascii=False, indent=2)


def main() -> None:
    """Hiển thị menu và điều phối các chức năng của chương trình."""
    expenses = load_expenses()

    while True:
        print("\n=== QUẢN LÝ CHI TIÊU ===")
        print("1. Thêm khoản chi")
        print("2. Xem khoản chi")
        print("3. Xem tổng theo danh mục")
        print("0. Lưu và thoát")
        choice = input("Bạn chọn: ").strip()

        # TODO: hoàn thiện từng nhánh menu theo Phần 4, 6, 8 và 10.
        if choice == "0":
            save_expenses(DATA_FILE, expenses)
            print("Đã lưu. Hẹn gặp lại!")
            break
        elif choice == "1":
            try:
                amount = parse_amount(input("Số tiền: "))
                category = input("Danh mục: ")
                note = input("Ghi chú: ")

                if not category:
                    print("Danh mục không được để trống.")
                    continue
                expense = make_expense(amount,category,note)
                expenses.append(expense)
                print("Đã thêm khoản chi.")
            except ValueError as error:
                print(f"Thông tin chưa hợp lệ: {error}")
        elif choice == "2":
            if not expenses:
                print("Chưa có khoản chi nào.")
            else:
                for number, expense in enumerate(expenses, start=1):
                    print(
                        f"{number}. {expense['category']} — "
                        f"{expense['amount']:,.0f} đồng — {expense['note']}"
                    )

        elif choice == "3":
            print(f"Tổng chi: {total_expenses(expenses):,.0f} đồng")

            for category, amount in totals_by_category(expenses).items():
                print(f"- {category}: {amount:,.0f} đồng")
        else:
            print("Lựa chọn không hợp lệ. Hãy nhập 1, 2, 3 hoặc 0.")


if __name__ == "__main__":
    main()
