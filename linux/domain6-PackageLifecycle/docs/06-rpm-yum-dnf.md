# Bài 6 — RPM, YUM và DNF

Ubuntu/Debian dùng `apt` và `dpkg`. Các hệ Fedora/RHEL thường dùng `dnf` hoặc `yum` và `rpm`.

## Mô hình

```text
dnf/yum → rpm → filesystem
```

- `rpm` là công cụ cấp thấp làm việc với package RPM và database cục bộ.
- `dnf`/`yum` là công cụ cấp cao làm việc với repository và dependency.

## Đối chiếu khái niệm

| Debian/Ubuntu | RPM-based |
|---|---|
| `.deb` | `.rpm` |
| `apt` | `dnf`/`yum` |
| `dpkg` | `rpm` |
| `/etc/apt/sources.list` | `/etc/yum.repos.d/` |
| package database Debian | RPM database |

Điều quan trọng trong LPIC không phải học thuộc rằng mọi lệnh giống nhau, mà hiểu cùng một workflow tồn tại ở hai hệ package khác nhau: tìm, cài, kiểm tra, cập nhật, gỡ và tìm file thuộc package.

## Signature và integrity

RPM ecosystem thường nhấn mạnh việc kiểm tra integrity và chữ ký package. Ý nghĩa chung là xác minh package không bị thay đổi ngoài ý muốn và đến từ nguồn tin cậy.

## Nguồn

- [LPIC-1 102.5 — RPM/YUM package management](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

