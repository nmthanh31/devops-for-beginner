# Bài 2 — Rsyslog, facilities và logrotate

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Đọc facility/priority/action của rsyslog.
> - Viết và test một config logrotate; biết `copytruncate` vs `postrotate` reopen.
>
> **Hình dung:** logrotate như thay cuộn giấy ghi chép đã đầy — cất cuộn cũ (rotate), nén lại (compress), vứt cuộn quá cũ (rotate N), và **báo người ghi** sang cuộn mới (signal/reopen) — nếu quên báo, họ vẫn ghi vào cuộn đã cất.


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

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Rotate xong là app ghi file mới." | App giữ FD cũ — cần `postrotate` gửi signal/reload, hoặc `copytruncate` ([L03 open-unlinked](../../domain3-Filesystem&Path/docs/04-open-unlinked-files.md)). |
| "`copytruncate` luôn an toàn." | Có thể mất vài dòng giữa copy và truncate. |
| "Sửa config logrotate là có hiệu lực ngay." | Chạy theo lịch; test bằng `logrotate -d` (dry run) / `-f`. |

## Tự kiểm tra

1. Sau rotate, `app.log` mới rỗng mãi, `app.log.1` vẫn lớn dần. Nguyên nhân?
2. Lệnh xem logrotate **sẽ** làm gì mà không làm thật?

<details>
<summary>Đáp án</summary>

1. App vẫn ghi vào FD của file cũ (đã đổi tên thành `.1`) — thiếu reopen.
2. `logrotate -d CONFIG`.

</details>

## Nguồn

- [LPIC-1 108.2 — System logging](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

