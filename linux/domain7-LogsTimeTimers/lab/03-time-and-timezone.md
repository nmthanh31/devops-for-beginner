# L07-03 — Kiểm tra system time và timezone

## Mục tiêu

Đọc system clock, UTC, timezone, NTP state và chrony source mà không thay đổi thời gian máy.

```bash
date
date -u
timedatectl
timedatectl show -p Timezone -p NTPSynchronized -p NTP
```

Nếu chrony có trên máy:

```bash
chronyc tracking
chronyc sources -v
```

## Explain-back

Viết ngắn: local time và UTC khác nhau thế nào; timezone có làm thay đổi thời điểm thực tế không; vì sao timer/log cần clock đúng; `NTPSynchronized` nói điều gì.

Không chạy `timedatectl set-time` hoặc thay đổi timezone trên VM dùng chung chỉ để làm bài.
