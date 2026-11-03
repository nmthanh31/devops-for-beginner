# Bài 5 — Systemd timers

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Viết cặp `.timer` + `.service`, phân biệt `OnCalendar` (realtime) và `OnBootSec`/`OnUnitActiveSec` (monotonic).
> - Chứng minh job **thành công**, không chỉ timer "active".


## Timer là gì?

Systemd timer là unit dùng để kích hoạt một service unit theo lịch hoặc sau một khoảng thời gian.

Mô hình:

```text
backup.timer → kích hoạt → backup.service
```

Timer nên tập trung vào lịch; service nên chứa command và policy chạy. Tách hai unit giúp kiểm tra, restart và reuse dễ hơn.

## Hai kiểu thời gian chính

- **OnCalendar:** chạy theo lịch wall-clock, ví dụ mỗi ngày vào một giờ nhất định.
- **OnBootSec/OnUnitActiveSec:** chạy sau khi boot hoặc sau khi unit được active một khoảng thời gian.

Timer có thể chạy ngay sau khi system boot nếu thời điểm lịch đã bị bỏ qua, tùy cấu hình `Persistent=`. Vì vậy cần hiểu policy thay vì chỉ nhìn chuỗi lịch.

## Timer không tự chứng minh job thành công

Timer active chỉ cho biết scheduler đang được nạp/chạy. Nó không có nghĩa service mà timer gọi đã thành công.

Phải kiểm tra cả:

```text
timer state → service invocation → service exit code → output/log
```

## Cron hay systemd timer?

Cron đơn giản và rất phổ biến. Systemd timer tích hợp tốt với service, dependency, journal, user/group và trạng thái systemd.

<!-- learn:tail -->
## Kiểm tra nhanh

```bash
systemd-analyze calendar 'Mon..Fri 02:30'      # kiểm biểu thức trước khi dùng
systemctl list-timers --all                      # NEXT / LAST
systemctl status backup.service                  # kết quả lần chạy cuối (exit code)
journalctl -u backup.service --since today
```

| Option | Tác dụng |
|---|---|
| `Persistent=true` | Chạy bù nếu máy tắt đúng lúc lịch |
| `RandomizedDelaySec=` | Rải tải, tránh mọi máy chạy cùng giây |
| `AccuracySec=` | Độ chính xác cho phép |

## Tự kiểm tra

1. `list-timers` thấy LAST hôm qua, nhưng không có file backup. Kiểm gì?
2. Máy tắt lúc 02:30, bật lúc 08:00. Job có chạy bù không?

<details>
<summary>Đáp án</summary>

1. `systemctl status backup.service` (exit code) + `journalctl -u backup.service` — timer đã kích hoạt nhưng service fail.
2. Chỉ khi `Persistent=true`.

</details>

## Nguồn

- [LPIC-1 107.2 — Scheduling jobs](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

