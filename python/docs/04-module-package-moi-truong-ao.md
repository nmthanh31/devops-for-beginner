# 04. Module, package và môi trường ảo

## Module

Mỗi file `.py` là một module có thể được import.

```python
import math
from pathlib import Path

print(math.sqrt(16))
print(Path("data") / "input.txt")
```

Tránh `from module import *` vì làm khó theo dõi nguồn gốc tên.

## Điểm bắt đầu của chương trình

```python
def main() -> None:
    print("Chương trình bắt đầu")


if __name__ == "__main__":
    main()
```

Điều kiện này giúp file vừa có thể chạy trực tiếp, vừa có thể được import mà không tự động chạy chương trình.

## Package

Package là thư mục chứa các module liên quan. Có thể dùng `__init__.py` để đánh dấu và cấu hình package.

Một cấu trúc đơn giản:

```text
my_app/
├── pyproject.toml
├── src/
│   └── my_app/
│       ├── __init__.py
│       └── cli.py
└── tests/
```

## Môi trường ảo

Môi trường ảo cô lập thư viện của từng dự án:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate
```

Sau đó cài dependency bằng `pip`:

```bash
python -m pip install requests
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

Không nên commit thư mục `.venv`. Hãy ghi dependency vào `requirements.txt` hoặc `pyproject.toml`.

## `pyproject.toml`

Đây là nơi hiện đại để mô tả project, dependency và cấu hình công cụ. Khi project lớn dần, nên dùng cấu trúc `src/` và package có tên rõ ràng.
