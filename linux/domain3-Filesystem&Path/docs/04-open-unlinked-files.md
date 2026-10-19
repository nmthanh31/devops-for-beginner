# Bài 4 — Open-unlinked: file đã xóa tên nhưng vẫn còn mở

> **Mở rộng vận hành:** đây không phải nội dung cốt lõi LPIC 104.6/104.7. Khái niệm này rất hữu ích khi điều tra vì sao log đã bị rotate/xóa nhưng disk space chưa được trả lại.

## “Xóa file” thực ra xóa gì?

Lệnh `rm file` gỡ tên file khỏi directory (unlink). Nếu đó là tên cuối cùng và không process nào còn mở file, filesystem có thể thu hồi dữ liệu. Nhưng nếu một process vẫn giữ file descriptor mở, kernel giữ object và dữ liệu cho tới khi descriptor cuối cùng được đóng.

~~~text
directory name bị unlink
       ↓
không còn path bình thường để mở lại
       ↓ nhưng process vẫn giữ FD
inode/data còn được giữ
       ↓ process close/exit
filesystem mới thu hồi dung lượng
~~~

Điều này giải thích trường hợp `du` không còn thấy file theo tên nhưng dung lượng filesystem chưa giảm. `df` tính dung lượng filesystem đã cấp phát; `du` đi qua các path đang tồn tại. Hai con số có thể lệch khi có open-unlinked file.

## Tìm evidence

~~~bash
lsof +L1
~~~

`+L1` chọn file đang mở có link count nhỏ hơn 1 (thường là file đã unlink nhưng còn mở). Có thể giới hạn theo PID: `lsof -p PID +L1`. Nếu không có `lsof`, kiểm tra `/proc/PID/fd/`; symlink tới file có thể hiện `(deleted)`.

Không tự kill một process production chỉ vì tìm thấy file deleted. Trước tiên xác định process, file, dung lượng, owner và quy trình restart/rotate phù hợp.

## Nguồn

- POSIX/Linux semantics: [`unlink(2)` — Linux man-pages](https://man7.org/linux/man-pages/man2/unlink.2.html)
- Công cụ evidence: [`lsof(8)` — Linux man-pages](https://www.man7.org/linux/man-pages/man8/lsof.8.html)

