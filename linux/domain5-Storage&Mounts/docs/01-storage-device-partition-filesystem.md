# Bài 1 — Block device, partition và filesystem

> **LPIC-1:** 104.1. Nội dung dưới đây giải thích quan hệ giữa thiết bị, vùng chia và filesystem; thao tác tạo partition/format chỉ làm trong lab riêng.

## Ba lớp khác nhau

### Block device: thiết bị chứa dữ liệu dạng khối

Kernel trình bày ổ đĩa hoặc thiết bị lưu trữ như một block device. Ví dụ: `/dev/sda`, `/dev/sdb`, `/dev/nvme0n1`. Chữ `b` hay tên `nvme0n1` chỉ là tên thiết bị mà hệ thống đang dùng; không nên giả định rằng một disk luôn có cùng tên sau khi phần cứng hoặc VM thay đổi.

### Partition: một vùng trên disk

Partition table mô tả cách chia disk thành các vùng. Ví dụ `/dev/sdb1` thường là partition đầu tiên trên `/dev/sdb`. Partition chỉ cho biết vùng nào được dành cho mục đích nào; nó chưa phải là nơi Linux có thể lưu file theo cấu trúc thư mục.

Các định dạng partition table phổ biến là **MBR** và **GPT**. GPT thường dùng trên hệ thống mới; MBR là định dạng cũ hơn. Cả hai đều mô tả ranh giới partition, không phải filesystem.

### Filesystem: cấu trúc tổ chức file

Filesystem được tạo trên một partition, logical volume hoặc thiết bị phù hợp. Nó tổ chức thư mục, file, metadata, quyền và vùng dữ liệu. Các ví dụ thường gặp là ext4, XFS, VFAT và exFAT.

Tạo filesystem (format) là thao tác ghi cấu trúc filesystem mới lên target. Nếu target đang chứa dữ liệu, thao tác này có thể làm dữ liệu cũ không còn truy cập được. Vì vậy “partition có tồn tại” không đồng nghĩa “filesystem đã có” và “format” không phải lệnh quan sát.

## Mô hình tổng quát

```text
/dev/sdb (disk)
└── /dev/sdb1 (partition)
    └── ext4 (filesystem)
```

Với LVM, sẽ có thêm các lớp ở giữa; xem [Bài 4 — LVM](./04-lvm-fundamentals.md).

## Cách đọc bằng chứng

`lsblk` trình bày cây block device và partition. Với `lsblk -f`, thêm thông tin filesystem, label, UUID và mount point. Đây là bước quan sát an toàn trước khi quyết định thao tác nào tiếp theo.

Điều quan trọng là nối đúng quan hệ: thiết bị cha → partition con → filesystem → mount point. Đừng suy ra loại filesystem chỉ từ tên `/dev/sdX`; hãy kiểm tra evidence.

## Nguồn

- [LPIC-1 104.1 — Create partitions and filesystems](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- Tham khảo lệnh: `man lsblk`, `man fdisk`, `man parted`, `man mkfs`.

