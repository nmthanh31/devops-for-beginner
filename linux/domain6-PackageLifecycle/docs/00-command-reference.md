# Domain 6 — Command reference

## Ubuntu/Debian — quan sát và tra cứu

| Lệnh | Ý nghĩa |
|---|---|
| `apt search <name>` | Tìm package theo tên/mô tả |
| `apt show <package>` | Xem metadata package |
| `apt list --installed` | Liệt kê package đã cài |
| `apt list -a <package>` | Xem các version có thể có |
| `dpkg -l` | Xem trạng thái package cục bộ |
| `dpkg -s <package>` | Xem status/version package |
| `dpkg -L <package>` | Xem các file package đã cài |
| `dpkg -S <path>` | Tìm package sở hữu file |
| `dpkg --audit` | Tìm package ở trạng thái bất thường |

## Ubuntu/Debian — thay đổi trạng thái

| Lệnh | Ý nghĩa |
|---|---|
| `sudo apt update` | Cập nhật danh sách package |
| `sudo apt install <package>` | Cài package và dependency |
| `sudo apt upgrade` | Nâng cấp package phù hợp |
| `sudo apt remove <package>` | Gỡ package, thường giữ config |
| `sudo apt purge <package>` | Gỡ package và config package |
| `sudo apt autoremove` | Gỡ dependency không còn cần; cần đọc danh sách trước |
| `sudo dpkg --configure -a` | Cấu hình package còn dang dở |
| `sudo apt --fix-broken install` | Cố gắng sửa dependency lỗi |

## RPM-based

| Lệnh | Ý nghĩa |
|---|---|
| `rpm -qa` | Liệt kê package RPM đã cài |
| `rpm -qi <package>` | Xem thông tin package |
| `rpm -ql <package>` | Xem file package cung cấp |
| `rpm -qf <path>` | Tìm package sở hữu file |
| `dnf search <name>` | Tìm package |
| `dnf info <package>` | Xem metadata |
| `sudo dnf install <package>` | Cài package |
| `sudo dnf upgrade` | Cập nhật package |
| `sudo dnf remove <package>` | Gỡ package |

## Quy tắc vận hành

Trước lệnh cài, upgrade, remove, purge hoặc autoremove:

1. Đọc danh sách thay đổi.
2. Kiểm tra package/service liên quan.
3. Xác nhận còn đủ disk space.
4. Biết cách verify và rollback nếu có lỗi.

