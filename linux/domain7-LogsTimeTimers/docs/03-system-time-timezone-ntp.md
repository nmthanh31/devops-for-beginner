# Bài 3 — System time, timezone và NTP

## Ba khái niệm dễ nhầm

- **System clock:** đồng hồ kernel đang dùng.
- **Hardware clock/RTC:** đồng hồ phần cứng của máy.
- **Timezone:** quy tắc hiển thị giờ địa phương từ một thời điểm chuẩn.

Timezone không làm thời gian thực sự trôi nhanh/chậm; nó thay đổi cách hiển thị và diễn giải timestamp.

## Vì sao system time quan trọng?

Time sai gây lỗi khó thấy:

- Log có timestamp không đúng thứ tự.
- Certificate bị coi là chưa có hiệu lực hoặc đã hết hạn.
- Cron/timer chạy sai thời điểm.
- TLS, token và distributed system gặp lỗi.

## NTP và chrony

NTP đồng bộ system clock với nguồn thời gian. `chrony` là một implementation thường dùng trên Linux; `chronyc` dùng để quan sát trạng thái đồng bộ.

Mô hình:

```text
time source/NTP server → chrony/ntpd → system clock
```

NTP không chỉ “set giờ một lần”; daemon có thể điều chỉnh clock dần để tránh nhảy thời gian đột ngột.

## Timezone

Linux dùng dữ liệu timezone trong `/usr/share/zoneinfo/`; cấu hình hiện tại thường liên quan tới `/etc/localtime` và `/etc/timezone` tùy distribution.

Khi ghi evidence, nên phân biệt timestamp hiển thị theo local timezone với timestamp UTC. Hai dòng có thể chỉ khác cách hiển thị chứ không phải hai thời điểm khác nhau.

## Nguồn

- [LPIC-1 108.1 — Maintain system time](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

