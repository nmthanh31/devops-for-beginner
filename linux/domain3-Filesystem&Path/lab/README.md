# L03 — Labs: Filesystem & Path

Hãy học các bài docs trước rồi mới làm lab. Các bài thực hành dùng file riêng dưới `$HOME` hoặc `/tmp`; không sửa config hệ thống, không ghi vào `/proc` hay `/sys`.

## Thứ tự

1. [Lab 1 — FHS scavenger hunt: tìm config, data, log](./01-fhs-scavenger-hunt.md)
2. [Lab 2 — Path lookup, inode và links](./02-path-inode-links.md)
3. [Lab 3 — Open-unlinked và dung lượng file](./03-open-unlinked.md)
4. [Lab 4 — Khám phá `/proc`, `/sys`, `/dev` (read-only)](./04-proc-sys-dev.md)

## Tiêu chí hoàn thành buổi

- Phân loại được config, log, application state, runtime state và command theo FHS.
- Dùng `find`/`type`/`whereis` phù hợp để tìm file/lệnh.
- Giải thích được hard link và symlink bằng inode/path evidence.
- Giải thích được vì sao file unlinked vẫn có thể chiếm dung lượng.
- Phân biệt vai trò `/proc`, `/sys`, `/dev` và chỉ đọc các interface trong lab.

