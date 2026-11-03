# Bài 3 — Hard link và symbolic link

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Tạo và nhận diện hard link, symlink; phân biệt chúng với copy bằng inode evidence.
> - Dự đoán điều gì xảy ra khi xóa tên gốc, khi đích nằm filesystem khác, khi symlink tương đối bị di chuyển.
>
> **Hình dung:** hard link = hai tên trong danh bạ cùng trỏ **một số điện thoại**; symlink = mẩu giấy ghi "xem tên X trong danh bạ" — nếu X bị xóa, mẩu giấy thành vô dụng (dangling).


> **LPIC-1 104.6:** tạo link, nhận diện hard/symbolic link, phân biệt copy với link và biết cách dùng link trong quản trị hệ thống.

## Hard link

Hard link là một tên directory khác cùng trỏ tới inode của file đó. Hai tên có metadata và nội dung chung vì chúng là hai tên của cùng object. Xóa một tên chỉ gỡ một directory entry; dữ liệu còn truy cập được qua tên hard link khác.

Thông thường hard link không đi qua filesystem khác và không tạo cho directory. Inode identity cần so sánh trong cùng filesystem.

~~~bash
ln original.txt hard.txt
~~~

## Symbolic link (symlink)

Symlink là một file riêng chứa đường dẫn tới đích. Khi truy cập symlink, kernel tiếp tục phân giải đường dẫn đó. Symlink có inode riêng; xóa symlink không xóa file đích. Symlink có thể trỏ qua filesystem khác, trỏ tới directory, và có thể bị dangling nếu đích mất.

~~~bash
ln -s original.txt symbolic.txt
readlink symbolic.txt
~~~

Symlink tương đối được diễn giải tương đối với thư mục chứa symlink, không phải thư mục hiện tại của người chạy lệnh.

## Link không giống copy

Copy tạo object và nội dung mới, thường có inode khác. Hard link tạo tên khác cho cùng inode. Symlink tạo object nhỏ riêng lưu path tới đích.

| Thuộc tính | Hard link | Symlink |
|---|---|---|
| Inode của link so với file đích | Cùng inode | Inode riêng |
| Đọc nội dung | Trực tiếp cùng file object | Đi theo path đích |
| Xóa tên gốc | Nội dung vẫn còn nếu còn hard link | Link có thể thành dangling |
| Qua filesystem khác | Không | Có thể |
| Đích là directory | Thường không cho phép | Có thể |

## Evidence

~~~bash
ls -li original.txt hard.txt symbolic.txt
stat -c 'device=%d inode=%i links=%h type=%F name=%n' original.txt hard.txt symbolic.txt
readlink symbolic.txt
namei -l symbolic.txt
~~~

Với hard link, `device` và `inode` của hai tên phải trùng trong cùng filesystem; link count thường tăng. Symlink có inode riêng và `readlink` in ra chuỗi path đích.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Xóa file gốc thì hard link mất nội dung." | Dữ liệu còn tới khi link count = 0 (và không ai mở). |
| "Symlink tương đối tính theo thư mục hiện tại của tôi." | Tính theo **thư mục chứa symlink**. |
| "Hard link là bản copy." | Cùng inode — sửa qua tên nào cũng thấy ở tên kia. |

## Tự kiểm tra

1. `ls -li` thấy `a.txt` và `b.txt` cùng inode, link count 2. `rm a.txt` thì `b.txt` ra sao?
2. `ln -s ../data/x /opt/app/x` rồi `mv /opt/app /srv/app`. Symlink còn đúng không?
3. Vì sao không tạo hard link từ `/home` sang `/mnt/usb`?

<details>
<summary>Đáp án</summary>

1. Vẫn đọc được bình thường; link count về 1.
2. Có thể sai — `../data/x` giờ tính từ `/srv/app`, tức `/srv/data/x`.
3. Hard link không vượt filesystem (inode chỉ có nghĩa trong một FS).

</details>

## Nguồn

- [LPIC-1 Objectives V5.0 — 104.6](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [LPI Learning Material 101, Version 5.0 — lesson 104.6](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf)
- Tham khảo lệnh: `man ln`, `man stat`, `man readlink`

