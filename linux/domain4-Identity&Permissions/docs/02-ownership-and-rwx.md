# Bài 2 — Ownership và quyền `rwx`

> **LPIC-1 104.5:** quản lý quyền truy cập file/thư mục và ownership; dùng group để chia sẻ quyền.

## Mỗi filesystem object có owner, group và mode

Ví dụ:

~~~text
-rw-r----- 1 appuser appteam 2048 app.conf
~~~

- `appuser`: owner.
- `appteam`: group owner.
- `rw-`: quyền của owner.
- `r--`: quyền của group.
- `---`: quyền của others.

Đổi ownership bằng `chown`/`chgrp`; đổi mode bằng `chmod`:

~~~bash
chown appuser:appteam app.conf
chmod 640 app.conf
~~~

Chỉ thực hiện thay đổi ownership thật trong phạm vi được phép; trên hệ thống bình thường `chown` thường cần root.

## Quyền trên regular file

- `r` — đọc nội dung.
- `w` — sửa/truncate nội dung.
- `x` — yêu cầu kernel thực thi file như chương trình (vẫn cần file phù hợp và các điều kiện khác).

## Quyền trên directory — phần thường gây nhầm

- `r` — liệt kê tên entry trong directory.
- `x` — search/traverse: đi qua directory và tra cứu entry bên trong.
- `w` — thay đổi danh sách tên, ví dụ tạo/xóa/đổi tên entry; thường cần đi cùng `x`.

Có `r` mà thiếu `x` có thể cho biết tên nhưng không cho phép truy cập metadata/nội dung entry theo path. Có `x` mà thiếu `r` có thể truy cập một tên đã biết nếu các điều kiện khác phù hợp, nhưng không liệt kê toàn bộ nội dung.

## `chmod` số và ký hiệu

Giá trị mỗi lớp: `r=4`, `w=2`, `x=1`. Ví dụ `640` nghĩa:

~~~text
owner: 6 = 4+2 = rw-
group: 4     = r--
other: 0     = ---
~~~

Số tương ứng chỉ là cách viết gọn mode bits; ký hiệu dễ đọc khi muốn đổi một phần:

~~~bash
chmod u=rw,g=r,o= file
chmod g+w file
chmod o-r file
~~~

## Kernel chọn một permission class

Với mode bits truyền thống, kiểm tra theo thứ tự:

1. Process effective UID có phải owner không? Nếu có, dùng **owner bits**.
2. Nếu không, effective/supplementary groups có khớp group owner không? Nếu có, dùng **group bits**.
3. Nếu không khớp, dùng **other bits**.

Không cộng dồn owner + group + other bits. Nếu process là owner nhưng owner bits không cho đọc, nó không “mượn” thêm quyền `other` để đọc.

ACL, capabilities và policy bảo mật khác có thể làm bức tranh đầy đủ phức tạp hơn; kiểm tra ACL khi output `ls -l` có dấu `+`.

## Nguồn

- [LPIC-1 Objectives V5.0 — 104.5](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [LPIC-1 Learning Material 101 — lesson 104.5](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf)
- Tham khảo: `man chmod`, `man chown`, `man chgrp`, `man inode`

