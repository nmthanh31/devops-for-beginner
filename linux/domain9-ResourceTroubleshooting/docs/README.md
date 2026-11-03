# L09 — Resource Troubleshooting · Theory

## Phạm vi và nguồn

Phần cốt lõi đối chiếu tài liệu chính thức của Linux Professional Institute:

- [LPIC-2 V4.5 — Objective 200.1](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5): đo CPU, memory, disk I/O; tìm process; liên hệ triệu chứng với nguyên nhân và xác định bottleneck.
- [LPIC-2 V5.0 draft — Objective 204.3](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V5.0): bổ sung systemd resource management và nhận thức về cgroups.
- [LPIC-1 V5.0 — Objectives 103.5 và 103.6](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0): process, signal, foreground/background và priority.

L09 chỉ tập trung vào **CPU, memory và disk I/O**. Network I/O được học riêng ở L10.

## Thứ tự học

1. [Mô hình chẩn đoán tài nguyên](./01-resource-troubleshooting-model.md)
2. [CPU, load average và process](./02-cpu-load-processes.md)
3. [Memory, cache, swap và OOM](./03-memory-swap-oom.md)
4. [Disk I/O, latency và process gây I/O](./04-disk-io.md)
5. [Liên hệ bằng chứng và tìm bottleneck](./05-correlating-bottlenecks.md)
6. [Baseline, lấy mẫu và capacity trend](./06-baseline-and-capacity.md)
7. [Giới hạn tài nguyên bằng systemd](./07-systemd-resource-control.md)
8. [Command reference](./00-command-reference.md)

## Mô hình tư duy

```text
                  ┌─ CPU: task có được chạy đủ nhanh không?
service chậm ─────┼─ memory: máy có phải reclaim/swap/OOM không?
                  └─ I/O: task có đang chờ storage không?

mỗi nhánh → host metric → process metric → log → kết luận
```

## Ba khái niệm phải phân biệt

- **Utilization:** tài nguyên bận bao nhiêu.
- **Saturation:** công việc có đang phải xếp hàng/chờ hay không.
- **Errors:** có lỗi, retry, timeout hoặc OOM hay không.

Tài nguyên bận cao chưa chắc đã gây sự cố. Dấu hiệu nguy hiểm hơn là có hàng đợi tăng, thời gian chờ tăng và triệu chứng của ứng dụng xảy ra cùng thời điểm.
