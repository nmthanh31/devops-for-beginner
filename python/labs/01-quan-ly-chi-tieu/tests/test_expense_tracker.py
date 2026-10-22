import json
import tempfile
import unittest
from pathlib import Path

from test_expense_tracker import (
    load_expenses,
    make_expense,
    parse_amount,
    save_expenses,
    total_expenses,
    totals_by_category,
)


class ExpenseTrackerTests(unittest.TestCase):
    def test_parse_amount_accepts_positive_number(self):
        self.assertEqual(parse_amount("45000"), 45000.0)

    def test_parse_amount_rejects_invalid_or_non_positive_values(self):
        for raw in ("abc", "0", "-10"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_amount(raw)

    def test_make_expense_returns_expected_dictionary(self):
        self.assertEqual(
            make_expense(45000.0, "Ăn uống", "Bữa trưa"),
            {"amount": 45000.0, "category": "Ăn uống", "note": "Bữa trưa"},
        )

    def test_totals(self):
        expenses = [
            make_expense(45000.0, "Ăn uống", "Bữa trưa"),
            make_expense(20000.0, "Di chuyển", "Gửi xe"),
            make_expense(15000.0, "Ăn uống", "Cà phê"),
        ]
        self.assertEqual(total_expenses(expenses), 80000.0)
        self.assertEqual(
            totals_by_category(expenses),
            {"Ăn uống": 60000.0, "Di chuyển": 20000.0},
        )

    def test_load_missing_file_returns_empty_list_and_round_trip_works(self):
        expenses = [make_expense(45000.0, "Ăn uống", "Bữa trưa")]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "expenses.json"
            self.assertEqual(load_expenses(path), [])
            save_expenses(path, expenses)
            self.assertEqual(load_expenses(path), expenses)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), expenses)


if __name__ == "__main__":
    unittest.main()
