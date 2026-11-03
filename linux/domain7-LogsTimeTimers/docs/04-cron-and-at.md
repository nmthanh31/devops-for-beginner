# Bài 4 — Cron và at

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Đọc/viết 5 trường cron và biết môi trường của cron khác shell của bạn.
> - Dùng `at` cho job một lần.


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

<!-- learn:tail -->
## Đọc 5 trường

```text
┌ phút (0-59)
│ ┌ giờ (0-23)
│ │ ┌ ngày trong tháng (1-31)
│ │ │ ┌ tháng (1-12)
│ │ │ │ ┌ thứ (0-7, 0 và 7 = CN)
│ │ │ │ │
30 2 * * 1-5  /usr/local/bin/backup.sh >> /var/tmp/backup.log 2>&1
→ 02:30 thứ Hai–Sáu
```

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Chạy tay được thì cron cũng được." | Cron có `PATH` tối giản, không có env/alias của shell, CWD khác. |
| "Output cron hiện ở đâu đó." | Gửi mail local hoặc mất — redirect vào file/journal. |
| "Cron dùng giờ local của tôi." | Dùng timezone của hệ thống/cron daemon. |

## Tự kiểm tra

1. `*/15 9-17 * * *` chạy khi nào?
2. Script chạy tay OK, trong cron báo `command not found`. Sửa thế nào?

<details>
<summary>Đáp án</summary>

1. Mỗi 15 phút, từ 09:00 tới 17:45, mọi ngày.
2. Dùng đường dẫn tuyệt đối hoặc đặt `PATH=` ở đầu crontab/script.

</details>

## Nguồn

- [LPIC-1 107.2 — Scheduling jobs](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

