# Bài 3 — `umask` và special permission bits

> **LPIC-1 104.5:** biết thay đổi file creation mask và nhận diện SUID, SGID, sticky bit.

## `umask`: giới hạn quyền mặc định khi tạo object

Chương trình yêu cầu mode cơ sở, sau đó `umask` loại bỏ các quyền bị mask. Cách nhớ phổ biến:

~~~text
file cơ sở:      666 (rw-rw-rw-)
directory cơ sở: 777 (rwxrwxrwx)
umask:           022
result file:     644 (rw-r--r--)
result dir:      755 (rwxr-xr-x)
~~~

Ở đây mask `022` loại quyền ghi của group và others. Chính xác hơn, quyền kết quả dựa trên mode mà ứng dụng yêu cầu và phép mask; không phải phép trừ số học đơn giản cho mọi mode.

Xem/đặt umask trong shell hiện tại:

~~~bash
umask
umask -S
umask 027
~~~

`umask 027` là thay đổi session shell hiện tại; shell con được tạo từ shell này thường kế thừa giá trị. Không đặt umask bừa trên host vì nó ảnh hưởng file mới của các lệnh tiếp theo.

## SUID — chạy executable với effective UID của owner

Trên executable phù hợp, SUID làm process nhận effective UID của owner file trong lúc chạy. Ví dụ cổ điển là một số tiện ích cần thao tác giới hạn. SUID root làm tăng rủi ro nếu chương trình có lỗi; đừng tự thêm SUID để “sửa permission”. Linux bỏ qua SUID trên script trong nhiều trường hợp bảo mật.

`ls -l` có thể hiện `s` ở vị trí execute của owner; dạng số có leading `4`, ví dụ `4755`.

## SGID — group identity / group inheritance

- Trên executable, SGID có thể làm process nhận effective GID của group owner.
- Trên directory, file/thư mục con thường kế thừa group owner của directory; directory con có thể tiếp tục kế thừa SGID tùy cách được tạo/filesystem.

Dạng số bắt đầu bằng `2`, ví dụ `2775` trên shared directory. Đây thường là cách phối hợp group cho thư mục dự án.

## Sticky bit — bảo vệ tên trong shared directory

Trong directory có sticky bit, user thường chỉ xóa/đổi tên entry do mình sở hữu (hoặc khi có quyền quản trị phù hợp), dù directory được chia sẻ và có quyền ghi. `/tmp` thường là ví dụ quen thuộc.

Dạng `ls -l` có `t` ở vị trí execute của others; dạng số bắt đầu bằng `1`, ví dụ `1777`.

## Nhận diện nhanh

~~~text
4xxx = SUID
2xxx = SGID
1xxx = sticky
~~~

Các bit này không thay thế việc hiểu owner/group/mode thường. Trước khi sửa, dùng `stat` để ghi baseline; trong production, xác định lý do bit đang tồn tại.

## Nguồn

- [LPIC-1 Objectives V5.0 — 104.5](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [LPIC-1 Learning Material 101 — lesson 104.5](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf)
- Tham khảo: `man umask`, `man chmod`, `man inode`

