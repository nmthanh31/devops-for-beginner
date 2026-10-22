# L06 Labs — Package Lifecycle

## Thứ tự

1. [L06-01 — Package lifecycle với `tree`](./01-package-lifecycle-tree.md)
2. [L06-02 — Điều tra package và mô phỏng thay đổi](./02-package-inventory-simulation.md)

## Quy tắc an toàn

- Đọc danh sách thay đổi trước khi xác nhận `apt install`, `remove`, `purge` hoặc `autoremove`.
- Không thử trên package hệ thống quan trọng như `systemd`, `openssh-server`, `sudo` hoặc kernel.
- Không xóa file thủ công trong `/usr`, `/bin` hoặc `/lib` để mô phỏng package lỗi.
- Lưu output command làm evidence nhưng không ghi password, token hoặc secret.
