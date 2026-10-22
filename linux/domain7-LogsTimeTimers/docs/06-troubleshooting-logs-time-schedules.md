# Bài 6 — Troubleshooting theo timestamp và evidence

## Câu hỏi đầu tiên

Khi job hoặc service không chạy, đừng bắt đầu bằng việc restart liên tục. Hãy xác định:

1. Lịch có được scheduler nhận không?
2. Thời gian/timezone của máy có đúng không?
3. Job được chạy bằng user nào?
4. Command có chạy trong environment/working directory nào?
5. Exit code và log nói gì?

## Chuỗi chẩn đoán

```text
clock/timezone
    ↓
timer/cron schedule
    ↓
service/process invocation
    ↓
exit code + stdout/stderr
    ↓
journal/syslog/application log
```

## Các lỗi thường gặp

### Job chạy sai giờ

Có thể do timezone, clock chưa đồng bộ hoặc bạn nhầm giờ local với UTC.

### Chạy tay được nhưng cron thất bại

Có thể do PATH, environment, working directory, quyền user hoặc shell khác.

### Timer active nhưng job không thành công

Timer chỉ kích hoạt service. Cần đọc status/log của service được gọi.

### Log không thấy

Có thể log đang ở journal thay vì `/var/log`, journal không persistent, filter sai thời gian/service, hoặc process ghi vào file khác.

## Evidence tối thiểu

Một incident pack nên có:

- Thời gian và timezone hiện tại.
- Lịch timer/cron.
- Trạng thái timer/service.
- Log theo service và khoảng thời gian.
- Exit code hoặc output của job.
- Kết quả verify sau khi sửa.

