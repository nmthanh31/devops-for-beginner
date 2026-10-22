# Bài 2 — Rsyslog, facilities và logrotate

## Rsyslog là gì?

Rsyslog là logging daemon phổ biến, có thể nhận, lọc, lưu hoặc chuyển log tới log server khác. `systemd-journald` và rsyslog có thể cùng xuất hiện trên một hệ thống.

Mô hình đơn giản:

```text
program/kernel/service → journald hoặc syslog message
                         ↓
                      rsyslog
                         ↓
                  file/remote server
```

## Facility, priority và action

Một syslog message thường được phân loại bởi:

- **Facility:** nguồn hoặc nhóm nguồn, ví dụ kernel, authentication, daemon, local use.
- **Priority:** mức độ như debug, info, warning, error, critical.
- **Action:** nơi xử lý, ví dụ ghi vào file, chuyển tới remote host hoặc bỏ qua.

Ba khái niệm này giúp cấu hình “log nào đi đâu”.

## Logrotate là gì?

Log file không thể tăng vô hạn. `logrotate` định kỳ:

- Đổi tên log hiện tại.
- Nén log cũ.
- Giữ lại một số vòng.
- Tạo file log mới.
- Có thể chạy postrotate để reload service.

Logrotate không phải backup dài hạn. Nó chỉ quản lý vòng đời các bản log cục bộ theo policy.

## Điểm cần chú ý

Sau khi rotate, process có thể vẫn giữ file descriptor tới file cũ. Tùy ứng dụng, cần reload/reopen log để process ghi vào file mới.

## Nguồn

- [LPIC-1 108.2 — System logging](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

