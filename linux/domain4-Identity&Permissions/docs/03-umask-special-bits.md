# Bài 3 — `umask` và special permission bits

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Tính mode mặc định từ `umask` (file từ 666, directory từ 777).
> - Nhận diện SUID, SGID, sticky trong `ls -l` và giải thích mỗi bit dùng để làm gì.
>
> **Hình dung:** `umask` là "bộ lọc" che bớt quyền khi tạo đồ mới. SUID là "mượn thẻ của chủ chương trình khi chạy" (như `passwd`), SGID trên thư mục là "đồ mới vào phòng tự mang nhãn nhóm của phòng", sticky là "trong phòng chung, chỉ chủ đồ mới được dọn đồ của mình" (`/tmp`).


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

<!-- learn:tail -->
## Bảng tính umask

| umask | File mới (từ 666) | Directory mới (từ 777) |
|---|---|---|
| `022` | `644` `rw-r--r--` | `755` `rwxr-xr-x` |
| `027` | `640` `rw-r-----` | `750` `rwxr-x---` |
| `077` | `600` `rw-------` | `700` `rwx------` |
| `002` | `664` `rw-rw-r--` | `775` `rwxrwxr-x` |

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "umask là phép trừ số học." | Là che bit (AND NOT); với giá trị thường gặp trông giống phép trừ. |
| "umask cho phép tạo file có `x`." | File thường bắt đầu từ 666 nên không tự có `x`. |
| "Chữ `S` hoa giống `s` thường." | `S` = bit đặt nhưng **không** có `x` bên dưới — thường là cấu hình sai. |

## Tự kiểm tra

1. umask `027`, tạo thư mục mới. Mode?
2. `ls -ld /tmp` → `drwxrwxrwt`. Chữ `t` nghĩa gì?
3. Thư mục dự án chung `drwxrws---`. File mới tạo bên trong thuộc group nào?

<details>
<summary>Đáp án</summary>

1. `750`.
2. Sticky bit: chỉ owner của file (hoặc owner dir/root) được xóa/đổi tên file đó.
3. Group của thư mục (SGID trên directory → kế thừa group).

</details>

## Nguồn

- [LPIC-1 Objectives V5.0 — 104.5](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [LPIC-1 Learning Material 101 — lesson 104.5](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf)
- Tham khảo: `man umask`, `man chmod`, `man inode`

