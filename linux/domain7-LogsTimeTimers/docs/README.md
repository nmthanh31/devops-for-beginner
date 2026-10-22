# L07 — Logs, Time & Timers · Theory

## Phạm vi và nguồn

Phần cốt lõi đối chiếu [LPIC-1 Objectives V5.0 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0):

- **107.2 — Automate system administration tasks by scheduling jobs:** cron, `at` và systemd timers.
- **108.1 — Maintain system time:** date/time, timezone, hardware clock, NTP và chrony.
- **108.2 — System logging:** journald, journalctl, rsyslog, facilities/priorities/actions, logrotate và log storage.

## Thứ tự học

1. [Logging overview và journald](./01-logging-journald.md)
2. [Rsyslog, facilities và logrotate](./02-rsyslog-logrotate.md)
3. [System time, timezone và NTP](./03-system-time-timezone-ntp.md)
4. [Cron và at](./04-cron-and-at.md)
5. [Systemd timers](./05-systemd-timers.md)
6. [Troubleshooting theo timestamp và evidence](./06-troubleshooting-logs-time-schedules.md)
7. [Command reference](./00-command-reference.md)

## Mô hình tư duy

```text
job/service xảy ra
        ↓
timestamp + message được ghi
        ↓
log được giữ/xoay vòng
        ↓
journalctl/grep đọc đúng evidence
        ↓
time/timer được kiểm tra để biết event xảy ra khi nào
```

