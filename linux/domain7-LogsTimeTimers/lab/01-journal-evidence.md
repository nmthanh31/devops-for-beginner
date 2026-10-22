# L07-01 — Tạo và lọc journal evidence

## Mục tiêu

Tạo một log marker, tìm nó theo message và thời gian, rồi giải thích log đang chứng minh điều gì.

### 1. Ghi marker

```bash
MARKER="l07-lab-$(date +%s)"
logger -t l07-lab "event=baseline marker=$MARKER result=ok"
printf 'Marker: %s\n' "$MARKER"
```

`logger` gửi message vào logging path; `-t` đặt tag để lọc.

### 2. Tìm log

```bash
journalctl -t l07-lab --since "5 minutes ago" --no-pager
journalctl --since "5 minutes ago" --grep="$MARKER" --no-pager
```

### 3. Thử priority

```bash
logger -p user.warning -t l07-lab "event=warning marker=$MARKER"
journalctl -t l07-lab -p warning --since "5 minutes ago" --no-pager
```

## DoD

- [ ] Tìm được message theo tag.
- [ ] Tìm được message theo marker.
- [ ] Phân biệt được facility, priority và tag.
