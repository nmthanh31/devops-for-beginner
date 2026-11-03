# Bài 2 — CPU, load average và process

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Đọc `%us/%sy/%wa/%st` và load average **so với số CPU**.
> - Biết load average Linux gồm cả task trạng thái `D` (chờ I/O) — load cao chưa chắc là CPU.
> - Tìm process/thread ăn CPU; hiểu nice ≠ giới hạn.


## CPU đang làm gì?

Trong `top`, `vmstat` hoặc `sar`, thời gian CPU thường được chia thành:

- `us`: chạy code ở user space.
- `sy`: chạy code kernel.
- `id`: CPU nhàn rỗi.
- `wa`: CPU idle trong lúc hệ thống còn công việc đang chờ I/O.
- `st`: thời gian VM muốn chạy nhưng hypervisor dành CPU cho VM khác.

CPU pressure thường đáng nghi khi `id` thấp kéo dài, hàng đợi runnable tăng và triệu chứng ứng dụng xảy ra cùng thời điểm.

## Load average là gì?

`uptime` hiển thị load trung bình trong 1, 5 và 15 phút.

Trên Linux, load không chỉ đếm task đang chạy hoặc chờ CPU. Nó còn gồm task ở trạng thái chờ không ngắt được, thường là trạng thái `D`, ví dụ chờ I/O kernel.

Vì vậy:

```text
load cao + CPU bận cao  → có thể CPU saturation
load cao + CPU còn idle → kiểm tra task D và I/O
```

So load với số logical CPU giúp tạo ngữ cảnh:

```bash
nproc
uptime
```

Nhưng đây chỉ là dấu hiệu ban đầu, không phải một ngưỡng tuyệt đối.

## Runnable queue

Trong:

```bash
vmstat 1
```

- `r`: số task runnable, đang chạy hoặc chờ CPU.
- `b`: số task bị block, thường đang chờ I/O.

Nếu `r` liên tục lớn hơn khả năng xử lý của CPU và `id` gần 0, CPU saturation là giả thuyết mạnh hơn. Nếu `b` cao, cần chuyển sang kiểm tra I/O.

## Tìm process dùng CPU

```bash
ps -eo pid,ppid,user,stat,ni,pri,%cpu,%mem,comm,args --sort=-%cpu
```

Các trường quan trọng:

- `pid`, `ppid`: process và parent process.
- `stat`: trạng thái process.
- `ni`, `pri`: nice value và priority.
- `%cpu`, `%mem`: mức sử dụng quan sát được.
- `comm`, `args`: tên chương trình và command line.

Một số trạng thái thường gặp:

- `R`: running hoặc runnable.
- `S`: sleeping, đang chờ một sự kiện bình thường.
- `D`: uninterruptible sleep, thường chờ I/O kernel.
- `T`: stopped.
- `Z`: zombie; process đã kết thúc nhưng parent chưa thu exit status.

`pstree -p` giúp nhìn quan hệ cha–con. `top -H -p PID` giúp xem thread trong một process.

## Nice không phải giới hạn CPU

`nice` và `renice` thay đổi mức ưu tiên CPU tương đối giữa các process cạnh tranh CPU. Chúng không đặt hard limit.

```bash
nice -n 10 command
sudo renice 10 -p PID
```

Nice value lớn hơn thường nghĩa là process nhường CPU nhiều hơn. Đừng thay priority trước khi xác định đúng PID và ghi lại giá trị ban đầu.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Load 8 là quá tải." | Tùy số CPU (`nproc`); 8 trên 16 core là nhàn. |
| "Load cao = CPU cao." | Task `D` chờ I/O cũng tính vào load. |
| "`renice` giới hạn CPU." | Chỉ đổi ưu tiên tương đối; giới hạn cứng dùng cgroup (Bài 7). |
| "`%st` cao là app lỗi." | Steal — hypervisor không cho VM đủ CPU. |

## Tự kiểm tra

1. `nproc`=4, load `6.0 5.8 5.5`, `top` thấy `%wa` 60%, `%us` 10%. CPU hay I/O?
2. Một process `Z` có tốn CPU không?

<details>
<summary>Đáp án</summary>

1. Nhiều khả năng **I/O** — CPU ít bận, nhiều thời gian chờ I/O; kiểm `vmstat` cột `b` và `iostat`.
2. Không — đã chết, chỉ chờ parent thu exit status.

</details>

## Nguồn

- [LPIC-2 V4.5 — Objective 200.1](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
- [LPIC-1 V5.0 — Objectives 103.5 và 103.6](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
