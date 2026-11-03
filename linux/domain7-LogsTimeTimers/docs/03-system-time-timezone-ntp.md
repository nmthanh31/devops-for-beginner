# Bài 3 — System time, timezone và NTP

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Phân biệt system clock (UTC), timezone (hiển thị), RTC, và trạng thái NTP sync.
> - Đọc `timedatectl` / `chronyc tracking`.
>
> **Liên hệ:** [N06 — clock lệch phá TLS](../../../network/domain06-DHCPDNSTime/docs/02-time-and-resolution-diagnosis.md).


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

<!-- learn:tail -->
## Tự kiểm tra

1. Đổi timezone có làm cert "not yet valid" hết lỗi không?
2. Hai máy log cùng sự kiện lệch 7 giờ đúng. Nghi gì trước?

<details>
<summary>Đáp án</summary>

1. Không — timezone chỉ đổi hiển thị.
2. Hiển thị timezone khác nhau (UTC vs +07), không phải clock lệch. So bằng `--utc`/`date -u`.

</details>

## Nguồn

- [LPIC-1 108.1 — Maintain system time](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

