# Bài 4 — Vòng đời package

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Đi trọn vòng: search → inspect → install → verify → remove/purge.
> - Phân biệt `remove` và `purge`; biết "cài xong" không có nghĩa "service đang chạy".


Một package thường đi qua chuỗi:

```text
Không có
  ↓
Tìm thấy trong repository
  ↓
Tải về
  ↓
Cài đặt
  ↓
Cấu hình
  ↓
Cập nhật
  ↓
Gỡ bỏ
```

## Tìm package

Trước khi cài, cần biết package có tên gì và repository có version nào.

## Cài package

Cài package thường làm nhiều việc hơn việc chép một executable:

- Đặt file vào filesystem.
- Tạo hoặc cập nhật config.
- Đăng ký service/unit nếu package cung cấp service.
- Tạo user/group nếu maintainer script yêu cầu.
- Ghi trạng thái vào package database.

## Cài package không đồng nghĩa service đang chạy

```text
package được cài
    ≠
service đang active
```

Sau khi cài package có service, cần kiểm tra riêng bằng systemd: service có tồn tại không, có active không, có enable không và process có hoạt động không.

## Remove và purge

```text
remove = gỡ chương trình, thường giữ một số cấu hình
purge  = gỡ chương trình và cấu hình do package quản lý
```

Dữ liệu ứng dụng trong `/var/lib`, `/var/log` hoặc thư mục riêng không nhất thiết bị xóa theo `remove` hay `purge`. Phải kiểm tra package và tài liệu cụ thể trước khi xóa dữ liệu.

## Update và upgrade

Update danh sách package và upgrade package là hai việc khác nhau. Trước khi xác nhận một upgrade, nên đọc danh sách package sẽ được thêm, nâng cấp hoặc gỡ.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`remove` xóa sạch." | Giữ config file; `purge` mới xóa config. |
| "Cài nginx là nginx đang phục vụ." | Kiểm `systemctl status`, `ss -lntp`, `curl` (L02). |
| "`autoremove` lúc nào cũng an toàn." | Đọc danh sách — có thể gỡ thứ bạn đang dùng mà chưa đánh dấu manual. |

## Tự kiểm tra

1. `dpkg -l tree` hiện `rc`. Nghĩa gì?
2. Sau `apt install nginx`, ba lệnh chứng minh service phục vụ được?

<details>
<summary>Đáp án</summary>

1. `r` = removed, `c` = config files còn lại — đã `remove` nhưng chưa `purge`.
2. `systemctl is-active nginx`, `ss -lntp | grep :80`, `curl -I http://127.0.0.1/`.

</details>

## Nguồn

- [LPIC-1 102.4/102.5 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

