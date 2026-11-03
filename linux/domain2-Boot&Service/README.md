# L02 — Boot & Service

> **Câu hỏi domain này trả lời:** Từ lúc bấm nút nguồn tới khi service phục vụ traffic gồm những bước nào — và khi service "chạy" mà vẫn lỗi, lần theo ra sao?

**Mô hình cần nhớ một câu:** *Firmware → GRUB → kernel → initramfs → systemd → target → service → process → socket → readiness; `active (running)` mới chỉ là bước thứ 8 trên 10.*

```text
Firmware → Bootloader → Kernel → initramfs → real root
     → systemd (PID 1) → target/dependencies → service
     → process → socket → application readiness
```

## Lộ trình

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [Boot flow](./docs/01-boot-flow.md) | 60′ | UEFI/BIOS, GRUB, kernel cmdline, initramfs |
| 2 | [systemd, unit, target](./docs/02-systemd-units-targets.md) | 30′ | Unit là gì, target là gì |
| 3 | [Dependency](./docs/03-dependencies.md) | 30′ | After vs Wants vs Requires |
| 4 | [Service unit](./docs/04-service-unit.md) | 40′ | User/WorkingDirectory/Environment, drop-in |
| 5 | [Lifecycle](./docs/05-service-lifecycle.md) | 30′ | start/enable, reload/daemon-reload, Restart= |
| 6 | [Type & readiness](./docs/06-startup-readiness.md) | 30′ | active ≠ listener ≠ healthy |
| 7 | [Journald](./docs/07-journald.md) | 25′ | Lọc log đúng unit/boot |
| 8 | [Troubleshooting & boot timing](./docs/08-troubleshooting-boot-timing.md) | 35′ | Thu evidence trước restart; critical-chain |
| — | [Bản đồ LPIC + tự kiểm tra cuối buổi (có đáp án)](./docs/README.md) | — | — |

## Lab

[Danh sách lab](./lab/README.md): viết user service đầu tiên · environment & restart policy.

## Đạt domain khi bạn có thể

- [ ] Viết, enable, vận hành và debug một service (unit + `systemd-analyze` + journal + HTTP proof).
- [ ] Giải thích và chứng minh active ≠ listener ≠ healthy.
- [ ] Phân biệt After/Wants/Requires, reload/daemon-reload, start/enable.
- [ ] Thu evidence đúng thứ tự trước khi restart.

## Liên kết

- Trước: [L01 Execution Model](../domain1-Execution%20model/README.md) · Tiếp theo: [L03 Filesystem & Path](../domain3-Filesystem&Path/README.md)
