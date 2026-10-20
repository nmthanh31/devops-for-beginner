# L06 — Linux Package Lifecycle

Domain này học cách quản lý vòng đời phần mềm trên Linux: tìm package, cài đặt, kiểm tra, cập nhật, xử lý dependency, rollback và gỡ bỏ.

## Theory

Đọc theo thứ tự trong [docs](./docs/README.md).

Nội dung chính bám theo LPIC-1 Objective **102.4 — Debian package management** và **102.5 — RPM/YUM package management**. Ubuntu/Debian dùng `apt` và `dpkg`; các hệ Fedora/RHEL thường dùng `dnf`/`yum` và `rpm`.

## Chuỗi cần nhớ

```text
repository → package → dependency → filesystem/config → service/process
```

Không chạy lệnh thay đổi package trên máy production nếu chưa kiểm tra package sẽ thêm, nâng cấp hoặc gỡ những gì.

