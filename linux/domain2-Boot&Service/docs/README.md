# L02 — Linux Boot & Service Management

Tài liệu Buổi 2 đi từ boot chain đến cách chẩn đoán một service không phục vụ traffic. Phần nền tảng được diễn giải theo mục tiêu LPIC-1; nội dung vận hành sâu hơn được giữ lại nhưng ghi rõ là **mở rộng**, không nhầm với phần thi cốt lõi. Mỗi bài có lab nhỏ hoặc bài tập tình huống.

Phần thực hành viết service tách riêng tại [Domain 2 Labs](../lab/README.md).

## Lộ trình

### Bản đồ theo LPIC-1

| Bài | Nền tảng chính thống | Phần mở rộng |
|---|---|---|
| 1. Boot flow | 101.2: boot sequence, BIOS/UEFI, bootloader, kernel, initramfs, init, log | boot image/cloud, timing |
| 2. systemd/unit/target | 101.2–101.3: systemd và boot target | unit types, locations, dependency graph |
| 3. Dependencies | 101.3: runlevel/target | Wants/Requires/After, readiness |
| 4. Service unit | 101.3: quản lý service/target | unit directives, process context, drop-in, user service |
| 5. Lifecycle | 101.3: đổi target, default target, shutdown/reboot, cảnh báo user, kết thúc process | reload, daemon-reload, restart policy |
| 6. Startup/readiness | 101.2–101.3: boot và service ở mức nền tảng | Type, socket, HTTP health |
| 7. Journald | 101.2: xem boot events bằng dmesg/journalctl | lọc log theo unit/boot |
| 8. Troubleshooting | 101.2–101.3: boot logs và target/service | systemd-analyze, điều tra nhiều lớp |

Tài liệu được viết lại cho dễ học, không chép nguyên văn giáo trình. Nguồn phạm vi chính là [LPIC-1 Objectives V5.0 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0) và [LPIC-1 Learning Material, Version 5.0](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf).

1. [Boot flow: Firmware đến systemd](./01-boot-flow.md)
2. [systemd, PID 1, unit và target](./02-systemd-units-targets.md)
3. [Dependency và thứ tự khởi động](./03-dependencies.md)
4. [Service unit và execution context](./04-service-unit.md)
5. [Lifecycle: start, enable, reload, restart](./05-service-lifecycle.md)
6. [Service type và readiness](./06-startup-readiness.md)
7. [Journald và log](./07-journald.md)
8. [Troubleshooting và boot timing](./08-troubleshooting-boot-timing.md)

## Mạch tư duy

~~~text
Firmware → Bootloader → Kernel → initramfs → real root
     → systemd (PID 1) → target/dependencies → service
     → process → socket → application readiness
~~~

## Kết quả cần đạt

Khi ứng dụng không hoạt động sau reboot, lần theo được:

~~~text
unit có được nạp và kích hoạt không?
        ↓
systemd tạo process nào?
        ↓
process chạy với context nào?
        ↓
process có socket đúng không?
        ↓
application có sẵn sàng không?
        ↓
journal và timing cho biết điều gì?
~~~

## Tự kiểm tra cuối buổi

1. Vai trò của firmware, bootloader, kernel, initramfs và systemd khác nhau thế nào?
2. Target khác service ra sao?
3. After khác Wants và Requires thế nào?
4. systemctl enable có start service ngay không?
5. daemon-reload khác reload thế nào?
6. active (running) có chứng minh HTTP healthy không?
7. Khi service failed, cần thu evidence nào trước khi restart?
