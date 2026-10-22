# Bài 5 — Cấu trúc script, cleanup và trap

## Shebang

Shebang ở dòng đầu cho biết interpreter:

```bash
#!/usr/bin/env bash
```

Script cũng cần quyền execute nếu muốn chạy trực tiếp, nhưng quyền execute không thay thế việc kiểm tra nội dung và interpreter.

## Strict mode

Một baseline thường dùng cho Bash script là:

```bash
set -Eeuo pipefail
```

- `-e`: dừng khi command thất bại trong nhiều ngữ cảnh.
- `-u`: báo lỗi khi dùng biến chưa được đặt.
- `pipefail`: pipeline báo lỗi nếu thành phần phù hợp bị lỗi.
- `-E`: giúp ERR trap được thừa hưởng trong một số ngữ cảnh.

Đây không phải “nút an toàn tuyệt đối”. `set -e` có các ngoại lệ theo ngữ cảnh `if`, `while`, `&&`, `||` và pipeline; vẫn phải thiết kế xử lý lỗi rõ ràng.

## Hàm và biến local

Chia script thành function nhỏ giúp giới hạn phạm vi và dễ test. Dùng `local` cho biến chỉ dùng trong function để tránh làm bẩn state bên ngoài.

## Trap và cleanup

`trap` cho phép chạy cleanup khi script nhận signal hoặc kết thúc. Một script tạo thư mục tạm, lock hoặc mount tạm nên có kế hoạch dọn dẹp khi thành công và khi thất bại.

```text
prepare → work → verify → commit
                 ↓ lỗi
              cleanup/rollback
```

## Idempotency

Script idempotent có thể chạy lại mà không làm hỏng trạng thái đã đúng. Ví dụ kiểm tra thư mục tồn tại trước khi tạo; không tạo duplicate entry mỗi lần chạy.

## Nguồn

- [LPIC-1 105.2 — Simple shell scripts](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

