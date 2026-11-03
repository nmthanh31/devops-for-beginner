# Bài 1 — Logging và systemd-journald

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Biết stdout/stderr của service đi vào journal thế nào.
> - Lọc journal theo **unit, boot, thời gian, priority** thay vì cuộn mù.
> - Phân biệt journal persistent và volatile.
>
> **Hình dung:** journal là hộp đen máy bay có chỉ mục — mỗi dòng gắn sẵn nhãn unit, PID, boot, mức độ. Sức mạnh nằm ở **lọc**, không ở đọc hết.


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

<!-- learn:tail -->
## Bộ lọc hay dùng

| Câu hỏi | Lệnh |
|---|---|
| Log của một unit | `journalctl -u lab-api.service` |
| Chỉ lần boot hiện tại / trước | `journalctl -b` / `journalctl -b -1` |
| Khoảng thời gian | `journalctl --since "2026-11-03 10:00" --until "10:15"` |
| Chỉ lỗi trở lên | `journalctl -p err` |
| Theo dõi trực tiếp | `journalctl -fu lab-api` |
| Kèm giải thích / không pager | `-x` / `--no-pager` |
| Giờ UTC | `--utc` |

## Tự kiểm tra

1. Service crash trước lần reboot vừa rồi. Lệnh xem log của nó ở boot đó?
2. `journalctl --list-boots` chỉ có 1 dòng dù máy đã reboot nhiều lần. Vì sao?

<details>
<summary>Đáp án</summary>

1. `journalctl -b -1 -u SERVICE`.
2. Journal volatile (`/run/log/journal`) — mất khi reboot; cần `/var/log/journal` + `Storage=persistent`.

</details>

## Nguồn

- [LPIC-1 108.2 — System logging](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

