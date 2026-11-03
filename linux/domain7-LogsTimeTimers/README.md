# L07 — Logs, Time & Timers

> **Câu hỏi domain này trả lời:** Chuyện gì đã xảy ra (log), nó xảy ra lúc nào (clock đúng không), và việc định kỳ có thật sự chạy và thành công không (cron/timer)?

**Mô hình cần nhớ một câu:** *Clock đúng → timestamp đáng tin → lọc log theo unit/boot/thời gian; lịch kích hoạt chưa chứng minh job thành công — luôn kiểm exit code và output.*

```text
event/process → log → query/filter → diagnosis
clock/timezone → timestamp đúng → log và scheduler đáng tin
schedule → job → output/log → verify
```

## Lộ trình

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [Logging & journald](./docs/01-logging-journald.md) | 30′ | Lọc theo unit/boot/time/priority |
| 2 | [rsyslog & logrotate](./docs/02-rsyslog-logrotate.md) | 30′ | Rotate và bẫy FD cũ |
| 3 | [Time, timezone, NTP](./docs/03-system-time-timezone-ntp.md) | 25′ | UTC vs hiển thị vs sync |
| 4 | [cron & at](./docs/04-cron-and-at.md) | 25′ | 5 trường; môi trường cron |
| 5 | [systemd timers](./docs/05-systemd-timers.md) | 30′ | OnCalendar, Persistent, chứng minh job OK |
| 6 | [Troubleshooting theo timestamp](./docs/06-troubleshooting-logs-time-schedules.md) | 25′ | Chuỗi evidence |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) | — | — |

## Lab

[Danh sách lab](./lab/README.md): journal evidence · user systemd timer · time & timezone · logrotate & bẫy FD cũ.

## Đạt domain khi bạn có thể

- [ ] Lấy log đúng boot/unit/khoảng thời gian bằng một lệnh `journalctl`.
- [ ] Rotate một log và giải thích (và sửa) bẫy app ghi file cũ.
- [ ] Viết timer + service, chứng minh job thành công bằng exit code + output.
- [ ] Giải thích UTC / timezone / NTP sync từ `timedatectl`.

## Liên kết

- Trước: [L06 Package Lifecycle](../domain6-PackageLifecycle/README.md) · Tiếp theo: [L08 Shell Safety](../domain8-ShellSafety/README.md)

## Nguồn

LPIC-1 [107.2, 108.1, 108.2](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
