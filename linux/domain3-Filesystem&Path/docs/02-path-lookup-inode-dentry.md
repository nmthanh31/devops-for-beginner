# Bài 2 — Path lookup, inode và dentry

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Mô tả kernel đi từng thành phần của path và chỗ path có thể hỏng giữa đường.
> - Phân biệt **tên** (directory entry), **inode** (object + metadata), **dentry** (cache trong VFS).
> - Đọc evidence bằng `stat`, `namei -l`, `readlink -f`.
>
> **Hình dung:** path giống chỉ đường "vào cổng → tầng 3 → phòng 302 → ngăn kéo 2". Tên phòng ghi trên cửa (directory entry), còn đồ vật thật trong ngăn kéo là inode. Một đồ vật có thể được ghi ở hai danh sách (hard link). Lễ tân nhớ sẵn các đường hay đi (dentry cache).


> **Nền tảng + mở rộng:** LPIC-1 104.7 yêu cầu tìm file và biết vị trí theo FHS. Inode là nền tảng cần để hiểu hard link trong 104.6. VFS path walk và dentry là phần mở rộng giải thích cách kernel tăng tốc việc tìm đường dẫn.

## Path là tên đường đi, không phải bản thân file

Ví dụ `/var/log/syslog` gồm các thành phần: `/` → `var` → `log` → `syslog`. Với path tuyệt đối, quá trình bắt đầu từ root directory `/`; với path tương đối, nó bắt đầu từ current working directory (CWD) của process.

Kernel phải lần lượt tra từng directory component, áp dụng quyền truy cập phù hợp, xử lý mount point và symbolic link, rồi tìm object cuối cùng. Vì vậy, một path có thể hỏng ở giữa đường: directory không tồn tại, quyền search bị chặn, hoặc symlink trỏ tới đích không còn tồn tại.

## Directory entry và inode

Trong filesystem kiểu Unix, directory chứa các ánh xạ tên → inode. Inode giữ metadata của object như loại file, owner, permissions, timestamps, kích thước, link count và vị trí dữ liệu theo cách filesystem quản lý. Tên path không được lưu thành “tên duy nhất” bên trong inode.

Một file có thể có nhiều tên hard link trỏ cùng inode. Do đó, inode number được xét cùng với filesystem/device chứa nó; cùng con số inode ở hai filesystem khác nhau không đồng nghĩa cùng một file.

## Dentry là gì? — phần mở rộng VFS

Dentry (directory entry cache) là object trong VFS cache giúp kernel ghi nhớ quan hệ giữa một tên trong directory với inode tương ứng. Có thể hình dung dentry như một mục tra cứu đã được cache trong lúc đi qua path. Nó không phải một “file dentry” mà bạn thường thấy bằng `ls` trên disk.

Mô hình dễ nhớ:

~~~text
path component: "syslog"
       ↓ tra trong directory "log"
dentry: tên + parent + liên hệ/cache tới inode
       ↓
inode: metadata/object của file trong filesystem
~~~

Chi tiết cấu trúc nội bộ và caching của VFS là kiến thức nâng cao; mục tiêu thực hành là đọc được evidence từ path, inode và symlink.

## Lệnh kiểm tra

~~~bash
stat /etc/os-release
stat -c 'device=%d inode=%i links=%h type=%F name=%n' /etc/os-release
namei -l /etc/os-release
readlink -f /etc/os-release
~~~

- `stat` hiển thị metadata của object ở path cuối.
- `namei -l` cho thấy từng thành phần của path và quyền/symlink khi đi qua.
- `readlink -f` cho biết path chuẩn hóa cuối cùng nếu các thành phần tồn tại.

GNU `stat path` mặc định hiển thị chính symlink nếu path cuối là symlink; thêm `stat -L path` để theo symlink và hiển thị metadata của đích. Khi cần xem target text, dùng `readlink link`.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Tên file nằm trong inode." | Tên nằm trong directory; inode không biết tên của mình. |
| "Cùng inode number là cùng file." | Chỉ khi cùng filesystem/device. |
| "Permission denied ở file cuối." | Có thể do thiếu quyền `x` ở một thư mục cha — `namei -l` chỉ ra. |
| "`stat link` cho metadata của đích." | GNU `stat` mặc định hiện chính symlink; dùng `stat -L`. |

## Tự kiểm tra

1. Path tương đối `logs/app.log` được tra bắt đầu từ đâu?
2. `cat /srv/app/conf/a.yml` báo Permission denied dù `a.yml` có mode `644`. Kiểm gì?
3. Dentry có phải một file trên disk không?

<details>
<summary>Đáp án</summary>

1. Từ CWD của process đang chạy lệnh.
2. `namei -l /srv/app/conf/a.yml` — một thư mục cha thiếu quyền search (`x`) cho user.
3. Không — là object cache trong bộ nhớ của VFS.

</details>

## Nguồn

- [LPIC-1 Objectives V5.0 — 104.6/104.7](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- Phần VFS path walk/dentry là mở rộng: [Linux kernel — Pathname lookup](https://docs.kernel.org/filesystems/path-lookup.html)
- Tham khảo lệnh: `man stat`, `man namei`, `man readlink`

