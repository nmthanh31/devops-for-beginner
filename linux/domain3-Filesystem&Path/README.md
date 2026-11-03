# L03 — Filesystem & Path

> **Câu hỏi domain này trả lời:** File nằm ở đâu, kernel tìm nó theo path thế nào, link khác copy ra sao, và vì sao file đã xóa vẫn chiếm dung lượng?

**Mô hình cần nhớ một câu:** *Path là tên đường đi → directory entry → inode; tên có thể mất mà object còn sống chừng nào còn link hoặc FD mở.*

## Lộ trình

| # | Bài | Thời lượng | Lab đi kèm |
|---|---|---|---|
| 1 | [FHS: config, data, log, command](./docs/01-fhs-file-locations.md) | 30′ | [Lab 1 — FHS scavenger hunt](./lab/01-fhs-scavenger-hunt.md) |
| 2 | [Path lookup, inode, dentry](./docs/02-path-lookup-inode-dentry.md) | 35′ | [Lab 2 — path, inode, links](./lab/02-path-inode-links.md) |
| 3 | [Hard link & symlink](./docs/03-hard-and-symbolic-links.md) | 30′ | (Lab 2) |
| 4 | [Open-unlinked](./docs/04-open-unlinked-files.md) | 25′ | [Lab 3 — open-unlinked](./lab/03-open-unlinked.md) |
| 5 | [/proc, /sys, /dev](./docs/05-proc-sys-dev.md) | 25′ | [Lab 4 — read-only](./lab/04-proc-sys-dev.md) |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) | — | — |

Tổng quan và ranh giới LPIC: [docs/README.md](./docs/README.md) · [lab/README.md](./lab/README.md).

## Đạt domain khi bạn có thể

- [ ] Tìm đúng config/data/log/runtime/executable của một service bằng `find`/`type`, giải thích theo FHS.
- [ ] Chứng minh hard link vs symlink bằng `stat`/`ls -li`/`readlink`/`namei`.
- [ ] Tìm và giải thích open-unlinked file (`lsof +L1`), giải thích `df` ≠ `du`.
- [ ] Đọc thông tin process/device từ `/proc`, `/sys`, `/dev` mà không ghi gì.

## Liên kết

- Trước: [L02 Boot & Service](../domain2-Boot&Service/README.md) · Tiếp theo: [L04 Identity & Permissions](../domain4-Identity&Permissions/README.md)
