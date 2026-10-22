# Domain 7 — Command reference

## Journal và logging

| Lệnh | Ý nghĩa |
|---|---|
| `journalctl -b` | Log của boot hiện tại |
| `journalctl -u <unit>` | Log của service/unit |
| `journalctl -p warning` | Lọc từ priority warning |
| `journalctl --since today` | Log từ đầu ngày |
| `journalctl -f` | Theo dõi log mới theo thời gian thực |
| `logger "message"` | Gửi một message vào syslog/journal path phù hợp |
| `systemctl status systemd-journald` | Xem trạng thái journald |
| `logrotate -d <config>` | Debug, không rotate thật |

## Time

| Lệnh | Ý nghĩa |
|---|---|
| `date` | Xem system time theo local timezone |
| `date -u` | Xem system time theo UTC |
| `timedatectl` | Xem time, timezone, NTP state |
| `timedatectl list-timezones` | Liệt kê timezone |
| `hwclock` | Xem/điều khiển hardware clock, cần cẩn thận |
| `chronyc tracking` | Xem trạng thái chrony |
| `chronyc sources` | Xem nguồn NTP |

## Cron và at

| Lệnh | Ý nghĩa |
|---|---|
| `crontab -l` | Xem crontab của user hiện tại |
| `crontab -e` | Sửa crontab của user hiện tại |
| `atq` | Xem job at đang chờ |
| `atrm <jobid>` | Xóa job at |

## Systemd timer

| Lệnh | Ý nghĩa |
|---|---|
| `systemctl list-timers` | Liệt kê timer system |
| `systemctl list-timers --all` | Bao gồm timer chưa active/đã chạy xong |
| `systemctl status <name>.timer` | Xem timer cụ thể |
| `systemctl cat <name>.timer` | Xem nội dung unit timer |
| `systemctl status <name>.service` | Xem service được timer gọi |

## Quy tắc vận hành

Trước khi sửa schedule hoặc log policy:

1. Ghi nhận clock/timezone hiện tại.
2. Xác định đúng scheduler và unit/job.
3. Đọc log trước khi restart.
4. Thay đổi một yếu tố mỗi lần.
5. Verify cả lịch, execution và output.

