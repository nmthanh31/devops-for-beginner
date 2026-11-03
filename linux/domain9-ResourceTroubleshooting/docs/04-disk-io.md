# Bài 4 — Disk I/O, latency và process gây I/O

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Phân biệt **dung lượng** (L05) và **hiệu năng I/O**.
> - Đọc `iostat -x`: `r/s w/s`, `r_await w_await`, `aqu-sz`, `%util`.
> - Tìm process gây I/O (`pidstat -d`, `iotop`) và hiểu trạng thái `D`.


## Dung lượng và hiệu năng là hai vấn đề khác nhau

Kiểm tra dung lượng trước:

```bash
df -h
df -i
```

- `df -h`: filesystem có hết byte hay không.
- `df -i`: filesystem có hết inode hay không.

Filesystem còn chỗ không có nghĩa là storage đang nhanh. Ngược lại, I/O chậm không nhất thiết do filesystem đầy.

## Quan sát từ `vmstat`

```bash
vmstat 1
```

Các trường liên quan:

- `b`: task bị block.
- `bi`: block đọc vào.
- `bo`: block ghi ra.
- `wa`: thời gian CPU idle trong khi còn I/O đang chờ.

`b` và `wa` tăng cùng thời điểm ứng dụng chậm là lý do để điều tra storage sâu hơn, chưa phải kết luận cuối cùng.

## Đọc `iostat`

```bash
iostat -xz 1
```

- `-x`: hiển thị thống kê mở rộng.
- `-z`: bỏ thiết bị không có hoạt động.
- `1`: lấy mẫu mỗi một giây.

Các trường thường dùng:

- `r/s`, `w/s`: số read/write request mỗi giây.
- `rkB/s`, `wkB/s`: throughput đọc/ghi.
- `await`: thời gian trung bình request chờ và được phục vụ.
- `aqu-sz`: độ dài hàng đợi trung bình.
- `%util`: tỷ lệ thời gian thiết bị có I/O đang hoạt động.

`await` và `aqu-sz` tăng cùng với latency ứng dụng là evidence mạnh hơn việc chỉ nhìn `%util`. Với SSD, RAID, SAN hoặc storage song song, `%util` không nên được hiểu máy móc là “100% thì chắc chắn hết công suất”.

## Tìm process gây I/O

```bash
sudo iotop -oPa
```

- `-o`: chỉ hiện process/thread đang có I/O.
- `-P`: gộp theo process.
- `-a`: tích lũy I/O thay vì chỉ nhìn một khoảnh khắc.

Có thể bổ sung:

```bash
pidstat -d 1
sudo lsof -p PID
```

`pidstat -d` cho biết I/O theo process. `lsof -p` cho biết process đang mở file/device nào, giúp nối process với path hoặc filesystem liên quan.

## Process ở trạng thái `D`

Task `D` đang chờ một thao tác kernel không ngắt được, thường liên quan I/O. Signal kill có thể đã được gửi nhưng task chỉ xử lý được sau khi thao tác kernel trở lại.

Vì vậy, “kill không được” không nhất thiết do thiếu quyền. Cần kiểm tra storage, filesystem, mount từ xa hoặc kernel log.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`%util` 100% là disk hết khả năng." | Với SSD/NVMe xử lý song song, `%util` không còn là thước đo bão hòa tin cậy; nhìn `await`, `aqu-sz`. |
| "Disk còn trống thì I/O ổn." | Dung lượng và latency là hai việc. |
| "Process `D` thì `kill -9` là xong." | `D` không nhận signal tới khi I/O xong. |

## Tự kiểm tra

1. `w_await` 250 ms trên SSD, `aqu-sz` 30. Nghĩa gì?
2. Lệnh tìm process ghi disk nhiều nhất mỗi giây?

<details>
<summary>Đáp án</summary>

1. Request ghi phải chờ rất lâu, hàng đợi dài → I/O saturation.
2. `pidstat -d 1` (hoặc `sudo iotop -o`).

</details>

## Nguồn

- [LPIC-2 V4.5 — Objective 200.1](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
