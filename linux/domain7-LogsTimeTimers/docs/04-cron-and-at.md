# Bài 4 — Cron và at

## Cron là gì?

Cron chạy command theo lịch lặp lại. Ví dụ: mỗi ngày, mỗi giờ hoặc vào một nhóm phút cụ thể.

Cron phù hợp với job đơn giản, định kỳ và không cần dependency phức tạp.

Các nguồn cấu hình thường gặp:

```text
/etc/crontab
/etc/cron.d/
/etc/cron.daily/
/etc/cron.hourly/
/var/spool/cron/
```

User crontab và system crontab có format khác nhau; system crontab thường có thêm trường user chạy job.

## Cron không chỉ là dòng lịch

Một job cron cần xác định:

- User chạy job.
- PATH và environment.
- Working directory.
- Output stdout/stderr đi đâu.
- File lock nếu job có thể chạy chồng.
- Cách log và kiểm tra exit code.

Shell interactive của bạn có environment khác cron. Một command chạy được trong terminal chưa chắc chạy được trong cron.

## at là gì?

`at` chạy job một lần tại thời điểm chỉ định. Nó khác cron vì không lặp lại.

```text
cron = lặp lại
at   = một lần
```

## Nguồn

- [LPIC-1 107.2 — Scheduling jobs](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

