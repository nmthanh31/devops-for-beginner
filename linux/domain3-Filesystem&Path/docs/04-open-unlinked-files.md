# Bài 4 — Open-unlinked: file đã xóa tên nhưng vẫn còn mở

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Giải thích vì sao `rm` một log lớn mà `df` không giảm.
> - Tìm process đang giữ file đã unlink bằng `lsof +L1` hoặc `/proc/PID/fd`.
> - Chọn cách xử lý an toàn (không kill bừa).
>
> **Hình dung:** bạn xóa tên một cuốn sách khỏi mục lục thư viện, nhưng một độc giả vẫn đang cầm nó đọc. Sách chỉ thật sự rời thư viện khi người đó trả lại (process đóng FD).
>
> **Cần trước:** [L01 File Descriptor](../../domain1-Execution%20model/docs/08-file-descriptor.md).


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

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`rm` giải phóng dung lượng ngay." | Chỉ khi không còn tên **và** không còn FD mở. |
| "`du` và `df` phải khớp." | `du` đếm theo path; `df` đếm theo FS — lệch khi có open-unlinked. |
| "Thấy `(deleted)` thì kill process." | Xác định process và quy trình restart/rotate trước. |

## Tự kiểm tra

1. Log 5 GB bị `rm`, `df` không đổi. Hai lệnh tìm thủ phạm?
2. Cách xử lý thường an toàn hơn kill khi đó là log của service?

<details>
<summary>Đáp án</summary>

1. `sudo lsof +L1` hoặc `ls -l /proc/*/fd 2>/dev/null | grep deleted`.
2. Restart/reload có kiểm soát service (để nó mở log mới), hoặc truncate qua FD (`: > /proc/PID/fd/N`) khi đã hiểu rủi ro; về lâu dài cấu hình logrotate đúng (`copytruncate` hoặc signal reopen — L07).

</details>

## Nguồn

- POSIX/Linux semantics: [`unlink(2)` — Linux man-pages](https://man7.org/linux/man-pages/man2/unlink.2.html)
- Công cụ evidence: [`lsof(8)` — Linux man-pages](https://www.man7.org/linux/man-pages/man8/lsof.8.html)

