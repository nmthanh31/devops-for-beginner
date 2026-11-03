# L09 — Resource Troubleshooting

> **Câu hỏi domain này trả lời:** Máy/service chậm vì **CPU**, **memory** hay **disk I/O** — và bằng chứng nào chứng minh, thay vì đoán rồi restart?

**Mô hình cần nhớ một câu:** *Đo từ host → process → log, cùng timestamp; cần dấu hiệu saturation (hàng đợi, chờ) chứ không chỉ utilization; ≥ 2 bằng chứng trước khi kết luận.*

```text
triệu chứng → phạm vi & thời điểm → đo CPU + memory + I/O → process liên quan
→ ≥ 2 bằng chứng → giả thuyết → minimal fix → positive + negative test
```

## Lộ trình

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [Mô hình chẩn đoán](./docs/01-resource-troubleshooting-model.md) | 20′ | USE; rộng → hẹp |
| 2 | [CPU, load, process](./docs/02-cpu-load-processes.md) | 35′ | Load so với `nproc`; `D` tính vào load |
| 3 | [Memory, swap, OOM](./docs/03-memory-swap-oom.md) | 35′ | `available`; `si/so`; bằng chứng OOM |
| 4 | [Disk I/O](./docs/04-disk-io.md) | 35′ | `iostat -x`; process `D` |
| 5 | [Ghép bằng chứng](./docs/05-correlating-bottlenecks.md) | 25′ | Bảng mẫu bottleneck |
| 6 | [Baseline & capacity](./docs/06-baseline-and-capacity.md) | 25′ | Interval, `sar`, xu hướng |
| 7 | [systemd resource control](./docs/07-systemd-resource-control.md) | 25′ | cgroup, `CPUQuota`, `MemoryMax` |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) · [Phạm vi LPIC](./docs/README.md) | — | — |
| Lab | [Baseline + 3 loại tải + bài mù](./lab/01-resource-baseline.md) | 90′ | — |

## Đạt domain khi bạn có thể

- [ ] Phân loại CPU / memory / I/O bằng `vmstat`/`free`/`iostat`/`pidstat` + journal, có before/after.
- [ ] Đọc load average đúng ngữ cảnh số CPU và trạng thái `D`.
- [ ] Tìm bằng chứng OOM kill.
- [ ] Giới hạn một service bằng cgroup và giải thích giới hạn ≠ sửa.

## Liên kết

- Trước: [L08 Shell Safety](../domain8-ShellSafety/README.md) · Tiếp theo: [L10 Host Networking](../domain10-HostNetworking/README.md)
