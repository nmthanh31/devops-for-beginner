# Domain 8 — Command reference

## Shell và environment

| Lệnh | Ý nghĩa |
|---|---|
| `command -v <cmd>` | Xem command sẽ được shell chọn |
| `type <cmd>` | Phân biệt alias/function/builtin/file |
| `env` | In environment của process |
| `export NAME=value` | Đưa biến vào environment của process con |
| `unset NAME` | Xóa biến |
| `source file` | Đọc file vào shell hiện tại |
| `printf '%q\n' "$value"` | Hiển thị giá trị theo dạng shell-escaped |

## Điều kiện và status

| Cú pháp | Ý nghĩa |
|---|---|
| `echo $?` | Xem status command ngay trước đó |
| `command && next` | Chạy `next` nếu command thành công |
| `command || fallback` | Chạy fallback nếu command thất bại |
| `if command; then ... fi` | Rẽ nhánh theo exit status |
| `test -e <path>` | Kiểm tra path tồn tại |
| `test -r/-w/-x <path>` | Kiểm tra read/write/execute |

## File và pipeline

| Lệnh/cú pháp | Ý nghĩa |
|---|---|
| `cmd > file` | Redirect stdout, ghi đè file |
| `cmd >> file` | Redirect stdout, append |
| `cmd 2> file` | Redirect stderr |
| `cmd >file 2>&1` | Gộp stdout và stderr vào file |
| `cmd1 | cmd2` | Nối stdout vào stdin |
| `tee file` | Vừa xem stdout vừa ghi file |
| `find ... -print0` | In pathname an toàn cho tên có khoảng trắng |

## Script safety

| Cú pháp | Ý nghĩa |
|---|---|
| `#!/usr/bin/env bash` | Chọn Bash interpreter |
| `set -Eeuo pipefail` | Baseline strict mode thường dùng |
| `trap 'cleanup' EXIT` | Chạy cleanup khi script kết thúc |
| `readonly VAR=value` | Đánh dấu biến không được gán lại |
| `shellcheck script.sh` | Phân tích tĩnh script nếu đã cài ShellCheck |

## Quy tắc trước command nguy hiểm

1. Quote biến chứa path.
2. Kiểm tra biến không rỗng.
3. Xác nhận target bằng `printf`, `ls` hoặc `find` trước.
4. Chạy dry-run nếu có thể.
5. Chỉ sau đó mới thêm action ghi/xóa/thay đổi quyền.

