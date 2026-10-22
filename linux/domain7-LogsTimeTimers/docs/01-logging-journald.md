# Bài 1 — Logging và systemd-journald

## Log là gì?

Log là bản ghi sự kiện: service khởi động, process lỗi, user đăng nhập, kernel phát hiện vấn đề hoặc một job chạy xong.

Log giúp trả lời:

- Chuyện gì đã xảy ra?
- Xảy ra lúc nào?
- Process/service nào tạo ra?
- Mức độ nghiêm trọng thế nào?
- Có lỗi lặp lại không?

## journald là gì?

`systemd-journald` thu thập log từ nhiều nguồn như service systemd, kernel và stdout/stderr của process do systemd quản lý. Dữ liệu được truy vấn bằng `journalctl`.

Journal là dữ liệu có trường metadata, không chỉ là một file text đơn giản. Vì vậy có thể lọc theo service, boot, thời gian, priority hoặc PID.

## Persistent và volatile journal

Journal có thể chỉ tồn tại trong RAM/temporary storage hoặc được lưu bền vững dưới `/var/log/journal/`. Nếu journal không persistent, một phần log có thể mất sau reboot.

Khi điều tra sự cố, cần biết log đang được lưu ở đâu và khoảng thời gian cần tìm còn tồn tại không.

## Priority

Log có mức độ từ thông tin thông thường tới lỗi nghiêm trọng. Lọc theo priority giúp giảm noise, nhưng không nên chỉ xem `error` rồi bỏ qua warning hoặc context trước đó.

## Nguyên tắc đọc log

Đừng chỉ đọc dòng cuối cùng. Hãy xem:

1. Sự kiện bắt đầu từ lúc nào.
2. Dòng đầu tiên báo lỗi thật sự.
3. Có restart/retry hay không.
4. PID, unit, user và timestamp có khớp không.

## Nguồn

- [LPIC-1 108.2 — System logging](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

