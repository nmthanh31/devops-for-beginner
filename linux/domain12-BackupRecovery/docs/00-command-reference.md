# L12 — Lệnh cần nhớ

| Lệnh | Vai trò |
|---|---|
| `findmnt --mountpoint PATH` | Xác nhận đúng filesystem ở mountpoint |
| `tar -czf ARCHIVE -C DIR .` | Đóng gói nội dung của DIR vào gzip archive |
| `tar -tzf ARCHIVE` | Liệt kê archive trước khi restore |
| `tar -xzf ARCHIVE -C DEST` | Restore vào DEST đã kiểm tra |
| `sha256sum ARCHIVE` | Tính hash archive |
| `sha256sum -c HASHFILE` | Đối chiếu hash đã lưu |
| `rsync -a --dry-run SRC/ DEST/` | Xem trước file sẽ đồng bộ |
| `stat FILE` | Kiểm tra owner, mode, size, timestamp |

`tar -C` đổi thư mục làm việc của tar trước khi đọc/giải nén; `-c` tạo archive, `-x` giải nén, `-t` liệt kê, `-z` gzip và `-f` chỉ định file archive. Dấu `/` cuối trong `rsync` ảnh hưởng việc đồng bộ **nội dung** thư mục hay chính thư mục đó; kiểm tra dry run trước.
