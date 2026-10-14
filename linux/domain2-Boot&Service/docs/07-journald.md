# Bài 7 — Journald và log của service

> **Nền tảng LPIC-1 101.2:** kiểm tra sự kiện boot qua log, gồm `dmesg` và `journalctl`. Lọc journal theo unit/boot và nối log với trạng thái service là phần hướng dẫn vận hành bổ sung.
>
> Nguồn: [LPI LPIC-1 Objectives V5.0](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0), mục 101.2; [LPIC-1 Learning Material (101), Version 5.0](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf).

## Mục tiêu

Hiểu đường đi của stdout/stderr khi app chạy dưới systemd và truy vấn journal theo unit, boot và thời gian.

## Log đi đâu?

Trong L01, process có:

~~~text
FD 0 → stdin
FD 1 → stdout
FD 2 → stderr
~~~

Khi application chạy dưới systemd, stdout/stderr có thể được nối vào journal tùy cấu hình.

~~~text
application stdout/stderr
          ↓
systemd journal stream
          ↓
systemd-journald
          ↓
journalctl truy vấn
~~~

journalctl là công cụ đọc/truy vấn; nó không khởi động service và không tự tạo log application.

## Log đến từ đâu?

Journal có thể chứa:

- stdout/stderr của application;
- thông báo từ systemd manager, như lỗi ExecStart hoặc timeout;
- metadata về unit, boot, thời gian và process liên quan.

Không phải mọi dòng đều do application in ra.

## Truy vấn thường dùng

~~~bash
journalctl -u nginx.service
journalctl -b -u nginx.service
journalctl -fu nginx.service
journalctl --list-boots
journalctl -u nginx.service -n 50 --no-pager
~~~

- -u lọc theo unit.
- -b chọn boot hiện tại.
- -f theo dõi log mới.
- --list-boots liệt kê các boot journal đang lưu.
- -n giới hạn số dòng cuối.

Journal có thể không lưu log qua reboot trên một số cấu hình; danh sách boot không đảm bảo toàn bộ lịch sử đều còn.

## Cách đọc log có hệ thống

1. Xác định đúng unit.
2. Chọn đúng boot hoặc khoảng thời gian.
3. Tìm lỗi đầu tiên, không chỉ dòng cuối.
4. Ghép log với Result, ExecMainStatus, MainPID và process evidence.
5. Sau khi có giả thuyết mới thay đổi hoặc restart.

## Lab 1 — Đọc journal của unit hiện có

~~~bash
systemctl list-units --type=service --state=running
journalctl -u <unit-name> -n 30 --no-pager
~~~

Ghi thời gian, dòng nào có vẻ do application phát ra, dòng nào do manager và có dấu hiệu start/stop/failure không. Nếu thiếu quyền đọc journal, ghi nhận thông báo; không đổi quyền hệ thống chỉ để làm lab.

## Lab 2 — Đọc journal của user service

Sau khi tạo user service ở bài service unit:

~~~bash
journalctl --user -u l02-lab-web.service -n 30 --no-pager
~~~

Nếu user journal không có sẵn, dùng Lab 1 và mô tả đường đi stdout/stderr theo cấu hình.

## Cần nhớ

Log service có thể đến từ application hoặc systemd manager. Lọc theo unit, boot và thời gian rồi ghép với runtime state.
