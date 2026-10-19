# Domain 5 — Linux Storage & Mounts

Mục tiêu của domain này là hiểu đường đi từ thiết bị lưu trữ tới thư mục mà ứng dụng sử dụng; biết phân biệt filesystem đầy dung lượng với đầy inode; và đọc được bằng chứng khi mount sai, mount thiếu hoặc storage đầy.

## Phạm vi và nguồn

Phần cốt lõi bám theo LPIC-1 Topic 104:

- **104.1 — Create partitions and filesystems:** MBR/GPT, partition và filesystem.
- **104.2 — Maintain filesystem integrity:** kiểm tra filesystem, theo dõi dung lượng và inode, sửa một số vấn đề cơ bản.
- **104.3 — Control mounting and unmounting:** mount/unmount, `/etc/fstab`, UUID/label và nhận biết systemd mount units.

LVM được giới thiệu ở mức khái niệm theo **LPIC-1 102.1 — Design hard disk layout**. Phần thao tác LVM sâu hơn là nội dung lab/mở rộng của roadmap, không nên nhầm với toàn bộ yêu cầu LPIC.

Nguồn chính: [LPIC-1 Objectives V5.0 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0). Mỗi bài ghi rõ phần LPIC tương ứng và phần giải thích/mở rộng.

## Thứ tự học

1. [Block device, partition và filesystem](./01-storage-device-partition-filesystem.md)
2. [UUID, mount point và mount/unmount](./02-uuid-mount-points.md)
3. [Dung lượng bytes, inode và filesystem đầy](./03-space-and-inodes.md)
4. [LVM: PV, VG và LV](./04-lvm-fundamentals.md)
5. [Mount bền vững, kiểm tra và phục hồi](./05-persistent-mounts-recovery.md)
6. [Command reference](./00-command-reference.md)
7. [Hướng dẫn thực hành: persistent mount và LVM](./06-persistent-mount-and-lvm-lab-guide.md)

## Mô hình cần nhớ

```text
Disk/block device → partition (hoặc LVM) → filesystem → UUID/label → mount point
```

Khi troubleshoot, đừng hỏi chung chung “ổ đĩa có vấn đề không?”. Hãy lần theo từng lớp: thiết bị nào được nhận diện, filesystem nào nằm trên đó, filesystem có được mount đúng chỗ không, và còn bytes/inode không.

## Ranh giới an toàn

Các lệnh quan sát như `lsblk`, `findmnt`, `df` và `blkid` phù hợp để thu evidence. Các lệnh tạo partition/filesystem như `fdisk`, `parted`, `mkfs` hoặc thay đổi LVM có thể làm mất dữ liệu nếu chọn sai thiết bị. Chỉ thực hành trên disk/VM lab đã xác nhận rõ; không chạy chúng trên disk hệ điều hành.

