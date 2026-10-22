# Bài 5 — Systemd timers

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

## Nguồn

- [LPIC-1 107.2 — Scheduling jobs](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

