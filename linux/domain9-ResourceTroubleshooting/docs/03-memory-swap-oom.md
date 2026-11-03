# Bài 3 — Memory, cache, swap và OOM

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Đọc `free` đúng: nhìn **available**, không nhìn `free`.
> - Nhận ra memory pressure (swap in/out, reclaim) và bằng chứng OOM kill.
> - Phân biệt leak (tăng dần) và spike (tăng vọt).
>
> **Hình dung:** RAM như bàn làm việc; page cache là tài liệu để sẵn trên bàn cho tiện — cần chỗ thì dẹp đi ngay. Bàn "đầy" vì tài liệu tham khảo không phải vấn đề; vấn đề là khi phải liên tục mang đồ ra kho (swap) rồi lấy lại.


## Vì sao `free` thấp chưa chắc là lỗi?

Linux tận dụng RAM chưa dùng làm page cache để tăng tốc đọc file. Cache này có thể được reclaim khi ứng dụng cần RAM.

```bash
free -h
```

Khi đọc output, ưu tiên nhìn:

- `available`: ước lượng RAM có thể cấp thêm mà chưa cần swap mạnh.
- `buff/cache`: RAM kernel đang dùng cho buffer/cache.
- `swap`: dung lượng swap đã dùng.

Không nên chỉ nhìn cột `free` rồi kết luận hết RAM.

## Memory pressure là gì?

Memory pressure xuất hiện khi kernel phải làm nhiều việc để tìm RAM có thể dùng:

- reclaim cache thường xuyên;
- ghi hoặc đọc page từ swap;
- ứng dụng allocation chậm hoặc thất bại;
- cuối cùng OOM killer có thể chọn process để kill.

Trong:

```bash
vmstat 1
```

- `si`: dữ liệu được đưa từ swap vào RAM.
- `so`: dữ liệu bị đẩy từ RAM ra swap.
- `swpd`: lượng swap đang được dùng.

Swap đã dùng không tự động có nghĩa là đang có sự cố. Dấu hiệu quan trọng hơn là `si`/`so` hoạt động liên tục cùng lúc ứng dụng chậm và `available` thấp.

## Tìm process dùng memory

```bash
ps -eo pid,ppid,user,%mem,rss,vsz,stat,comm,args --sort=-rss
```

- `RSS`: phần bộ nhớ vật lý process đang cư trú trong RAM.
- `VSZ`: không gian địa chỉ ảo; có thể rất lớn nhưng không đồng nghĩa process đang chiếm từng đó RAM vật lý.
- `%MEM`: tỷ lệ memory theo cách `ps` tính tại thời điểm lấy mẫu.

Đừng cộng RSS của nhiều process một cách máy móc đối với ứng dụng dùng shared memory hoặc shared libraries.

## OOM killer

Khi không thể cấp phát memory, kernel có thể dùng Out-Of-Memory killer để kết thúc một process nhằm cứu hệ thống.

Kiểm tra kernel log:

```bash
sudo journalctl -k -g 'oom|out of memory|killed process' --no-pager
```

Nếu thấy service “tự nhiên chết”, cần đối chiếu:

1. timestamp service dừng;
2. kernel OOM log;
3. memory/swap trước sự cố nếu có `sar` hoặc monitoring;
4. process/cgroup bị kill.

## Memory leak và spike khác nhau

- **Spike:** memory tăng nhanh rồi giảm sau khi công việc kết thúc.
- **Leak hoặc giữ cache phía ứng dụng:** memory tăng dần qua thời gian và không quay lại baseline phù hợp.

Một ảnh chụp tại một thời điểm không phân biệt được hai trường hợp này. Cần lấy mẫu nhiều lần hoặc xem dữ liệu lịch sử.

<!-- learn:tail -->
## Bằng chứng OOM

```bash
journalctl -k | grep -iE 'out of memory|oom-kill|killed process'
systemctl status SERVICE        # "status=9/KILL" / "oom-kill"
```

## Tự kiểm tra

1. `free -h`: free 200Mi, available 5Gi. Có thiếu RAM không?
2. `vmstat 1`: cột `si`/`so` liên tục > 0. Nghĩa gì?
3. Service tự restart, exit `9/KILL`. Lệnh xác nhận OOM?

<details>
<summary>Đáp án</summary>

1. Không — phần lớn là cache có thể thu hồi.
2. Đang swap in/out liên tục → memory pressure thật.
3. `journalctl -k | grep -i oom` (kèm thời điểm khớp).

</details>

## Nguồn

- [LPIC-2 V4.5 — Objective 200.1](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
