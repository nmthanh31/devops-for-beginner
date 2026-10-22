# L07-02 — User systemd timer ghi timestamp

## Mục tiêu

Tạo service và timer ở user scope. Timer chạy service định kỳ; service ghi timestamp vào file lab.

### 1. Tạo thư mục

```bash
mkdir -p "$HOME/l07-timer-lab"
mkdir -p "$HOME/.config/systemd/user"
```

Tạo `~/.config/systemd/user/l07-heartbeat.service`:

```ini
[Unit]
Description=L07 timer heartbeat service

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'printf "run=%s\n" "$(date --iso-8601=seconds)" >> "$HOME/l07-timer-lab/heartbeat.log"'
```

Tạo `~/.config/systemd/user/l07-heartbeat.timer`:

```ini
[Unit]
Description=Run L07 heartbeat every minute

[Timer]
OnBootSec=30s
OnUnitActiveSec=60s
Unit=l07-heartbeat.service

[Install]
WantedBy=timers.target
```

### 2. Nạp và chạy timer

```bash
systemctl --user daemon-reload
systemctl --user start l07-heartbeat.timer
systemctl --user status l07-heartbeat.timer --no-pager
systemctl --user list-timers --all | grep l07-heartbeat
```

### 3. Kiểm tra service và log

Chờ khoảng một phút:

```bash
cat "$HOME/l07-timer-lab/heartbeat.log"
systemctl --user status l07-heartbeat.service --no-pager
journalctl --user -u l07-heartbeat.service --since "5 minutes ago" --no-pager
```

Timer active chỉ chứng minh scheduler đang hoạt động; file và journal mới chứng minh service thực sự được chạy.

### Cleanup

```bash
systemctl --user stop l07-heartbeat.timer
systemctl --user disable l07-heartbeat.timer 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/l07-heartbeat.timer" "$HOME/.config/systemd/user/l07-heartbeat.service"
systemctl --user daemon-reload
```

## DoD

- [ ] Giải thích được timer → service.
- [ ] Tìm được lần chạy trong journal.
- [ ] Phân biệt timer active với service thành công.
- [ ] Cleanup không đụng system unit.
