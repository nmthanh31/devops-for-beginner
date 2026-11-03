# L05 — Storage & Mounts

> **Câu hỏi domain này trả lời:** Từ một disk tới thư mục ứng dụng dùng gồm những lớp nào, làm sao mount bền vững qua reboot, và "đầy disk" là đầy bytes hay đầy inode?

**Mô hình cần nhớ một câu:** *Disk → partition/LVM → filesystem → UUID → mount point; troubleshoot theo từng lớp, và luôn `findmnt --verify` trước khi reboot.*

## Lộ trình

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [Block device, partition, filesystem](./docs/01-storage-device-partition-filesystem.md) | 25′ | Ba lớp khác nhau thế nào? |
| 2 | [UUID & mount](./docs/02-uuid-mount-points.md) | 25′ | Vì sao UUID? Dữ liệu bị che dưới mount point? |
| 3 | [Bytes & inode](./docs/03-space-and-inodes.md) | 25′ | Đầy loại nào? `df` ≠ `du`? |
| 4 | [LVM PV/VG/LV](./docs/04-lvm-fundamentals.md) | 25′ | Mở rộng là chuỗi nhiều lớp |
| 5 | [Mount bền vững & phục hồi](./docs/05-persistent-mounts-recovery.md) | 30′ | `fstab`, `nofail`, emergency mode |
| Lab | [Persistent mount & LVM (có hướng dẫn loop device)](./docs/06-persistent-mount-and-lvm-lab-guide.md) | 90′ | Làm thật, có rollback |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) · [Phạm vi LPIC & an toàn](./docs/README.md) | — | — |

## Đạt domain khi bạn có thể

- [ ] Mount bền vững bằng UUID, kiểm bằng `findmnt --verify` và mount lại.
- [ ] Tạo PV/VG/LV, filesystem, mount, và mở rộng có `-r`.
- [ ] Phân biệt đầy bytes / đầy inode / open-unlinked / dữ liệu bị che.
- [ ] Phục hồi được khi `fstab` sai (biết đường console + emergency shell).

> ⚠️ `fdisk`, `parted`, `mkfs`, `pvcreate` chỉ chạy trên disk/loop lab đã xác minh.

## Liên kết

- Trước: [L04 Identity & Permissions](../domain4-Identity&Permissions/README.md) · Tiếp theo: [L06 Package Lifecycle](../domain6-PackageLifecycle/README.md)
