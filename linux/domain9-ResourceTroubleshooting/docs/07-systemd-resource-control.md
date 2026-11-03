# Bài 7 — Giới hạn tài nguyên bằng systemd

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Biết systemd đặt mỗi service vào một cgroup và quan sát bằng `systemd-cgtop`, `systemctl status`.
> - Đặt `CPUQuota`, `MemoryMax`, `IOWeight`… và hiểu **giới hạn ≠ sửa bottleneck**.


> Đây là phần mở rộng cần thiết cho vận hành hiện đại. Nội dung này xuất hiện trong bản dự thảo LPIC-2 V5.0 Objective 204.3.

## Cgroup và systemd liên quan thế nào?

Linux cgroup nhóm process và theo dõi hoặc giới hạn tài nguyên của nhóm đó. Systemd đặt service, scope và slice vào hierarchy cgroup.

```text
system.slice
    └── example.service
            ├── main process
            └── child processes
```

Nhờ vậy, giới hạn áp dụng cho toàn service thay vì chỉ một PID có thể thay đổi sau restart.

## Quan sát hierarchy và mức sử dụng

```bash
systemd-cgls
systemd-cgtop
systemctl status example.service
systemctl show example.service
```

- `systemd-cgls`: xem cây cgroup.
- `systemd-cgtop`: xem CPU, memory và I/O theo cgroup.
- `systemctl show`: xem thuộc tính thực tế systemd đã nạp.

## Các nhóm cấu hình chính

CPU:

```ini
CPUWeight=100
CPUQuota=50%
```

- `CPUWeight`: ưu tiên tương đối khi các nhóm cùng tranh CPU.
- `CPUQuota`: đặt giới hạn CPU theo thời gian.

Memory:

```ini
MemoryHigh=500M
MemoryMax=700M
```

- `MemoryHigh`: ngưỡng pressure/throttling mềm để service tự điều chỉnh.
- `MemoryMax`: giới hạn cứng; đặt quá thấp có thể dẫn tới OOM trong cgroup.

I/O:

```ini
IOWeight=100
```

`IOWeight` là trọng số tương đối giữa các cgroup khi cùng tranh I/O trên thiết bị hỗ trợ phù hợp.

## Giới hạn không phải là sửa bottleneck

Resource control bảo vệ host và service khác khỏi một workload quá mức. Nó không làm một ứng dụng cần 2 CPU chạy nhanh hơn khi bị giới hạn ở 0.5 CPU.

Trước khi đặt giới hạn:

1. đo baseline;
2. xác định service và workload;
3. đặt giá trị có headroom;
4. reload/restart có kiểm soát;
5. kiểm tra chức năng, latency, OOM và throttling;
6. chuẩn bị rollback.

<!-- learn:tail -->
## Tự kiểm tra

1. Đặt `MemoryMax=200M` cho service đang leak. Điều gì xảy ra khi nó vượt?
2. Lệnh thử giới hạn tạm thời không sửa file unit?

<details>
<summary>Đáp án</summary>

1. Bị OOM-kill **trong cgroup của nó** (không ảnh hưởng cả host) — nhưng leak vẫn còn, chỉ là bị chặn.
2. `systemctl set-property --runtime SERVICE MemoryMax=200M` hoặc `systemd-run -p MemoryMax=200M CMD`.

</details>

## Nguồn

- [LPIC-2 V5.0 draft — Objective 204.3 Resource Management](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V5.0)
