# L03 — Linux Filesystem & Path

Buổi này học cách tìm đúng file theo vai trò của nó, lần theo một path, hiểu inode/link và thu evidence khi file có vẻ đã bị xóa nhưng vẫn chiếm dung lượng.

## Nguồn và ranh giới LPIC

Phần cốt lõi bám theo [LPIC-1 Objective 104.6](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0) về hard/symbolic links và [104.7](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0) về FHS, vị trí file và tìm file/lệnh. LPI liệt kê `ln`, `ls`, `find`, `locate`, `updatedb`, `whereis`, `which`, `type` trong các objective tương ứng.

`dentry`, VFS path walk, `namei`, `stat`, `/proc`, `/sys`, `/dev`, `lsof` và open-unlinked được giữ như phần đào sâu/ứng dụng vận hành, không được gán nhầm là toàn bộ kiến thức LPIC 104.6/104.7.

| Phần | Liên hệ objective |
|---|---|
| FHS, tìm file và command | LPIC 104.7 |
| Hard link, symbolic link, copy-vs-link | LPIC 104.6 |
| Inode, dentry, path walk, `namei`/`stat` evidence | Mở rộng để giải thích/kiểm chứng links và path |
| Open-unlinked, `lsof +L1` | Mở rộng vận hành |
| `/proc`, `/sys`, `/dev` | Bổ sung để nhận diện cây file-like interface của Linux |

## Lộ trình

1. [FHS: tìm config, data, log và command](./01-fhs-file-locations.md)
2. [Path lookup, inode và dentry](./02-path-lookup-inode-dentry.md)
3. [Hard link và symbolic link](./03-hard-and-symbolic-links.md)
4. [Open-unlinked: file đã unlink nhưng process vẫn mở](./04-open-unlinked-files.md)
5. [/proc, /sys và /dev](./05-proc-sys-dev.md)
6. [Command reference](./00-command-reference.md)

## Mạch tư duy

~~~text
path: /etc/app/config.yaml
   ↓ đi từng directory component
directory entry (tên) → inode (metadata/object trong filesystem)
   ↓ process mở file
file descriptor → open file vẫn có thể tồn tại dù tên bị unlink
~~~

## Labs

Học xong lý thuyết mới làm [L03 Labs](../lab/README.md), theo thứ tự: tìm file theo FHS → phân tích path và links → open-unlinked → nhận diện pseudo-filesystems.

