# L06 — Package Lifecycle

> **Câu hỏi domain này trả lời:** Phần mềm đến từ đâu, cài vào đâu, phụ thuộc gì — và làm sao update, giữ version, rollback hay gỡ có kiểm soát?

**Mô hình cần nhớ một câu:** *Repository → package (file + metadata + dependency) → filesystem/config → service; APT lo repo và dependency, dpkg giữ sổ kho cục bộ — luôn mô phỏng (`-s`) và đọc kế hoạch trước khi `Y`.*

## Lộ trình

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [Package, repository, metadata](./docs/01-package-repository-metadata.md) | 25′ | `apt update` làm gì? |
| 2 | [APT & dependency](./docs/02-apt-repository-dependencies.md) | 25′ | upgrade vs full-upgrade; mô phỏng |
| 3 | [dpkg & database](./docs/03-dpkg-package-database.md) | 25′ | `-s` / `-L` / `-S` |
| 4 | [Vòng đời package](./docs/04-package-lifecycle.md) | 30′ | remove vs purge; cài ≠ chạy |
| 5 | [Repair & rollback](./docs/05-package-repair-rollback.md) | 30′ | Khoanh lớp lỗi; hold/pin/rollback |
| 6 | [RPM / DNF](./docs/06-rpm-yum-dnf.md) | 15′ | Bảng đối chiếu |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) | — | — |

## Lab

1. [Vòng đời với `tree`](./lab/01-package-lifecycle-tree.md) — 45′
2. [Inventory & mô phỏng](./lab/02-package-inventory-simulation.md) — 30′
3. [Hold, rollback, remove vs purge](./lab/03-pin-and-rollback.md) — 45′

Quy tắc an toàn: [lab/README.md](./lab/README.md).

## Đạt domain khi bạn có thể

- [ ] Cài, verify (status/file list/owner), gỡ một package và giải thích từng bước.
- [ ] Tìm package sở hữu một file; nhận ra file **không** do package quản lý.
- [ ] Hold/pin và rollback version (hoặc chứng minh vì sao không được).
- [ ] Sửa trạng thái dpkg gián đoạn bằng `dpkg --configure -a` / `apt -f install`.

## Liên kết

- Trước: [L05 Storage & Mounts](../domain5-Storage&Mounts/README.md) · Tiếp theo: [L07 Logs, Time & Timers](../domain7-LogsTimeTimers/README.md)
