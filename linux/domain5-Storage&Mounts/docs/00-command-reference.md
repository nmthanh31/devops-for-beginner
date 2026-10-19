# Domain 5 — Command reference

## Quan sát an toàn

| Lệnh | Ý nghĩa |
|---|---|
| `lsblk` | Cây block device/partition |
| `lsblk -f` | Thêm filesystem, label, UUID và mount point |
| `blkid` | Nhận diện filesystem, UUID và loại filesystem trên thiết bị |
| `findmnt` | Xem filesystem/source đang mount tại đâu |
| `findmnt --target /data` | Xác định filesystem phục vụ đường dẫn `/data` |
| `df -h` | Dung lượng bytes theo đơn vị dễ đọc |
| `df -i` | Mức sử dụng inode |
| `du -sh /path` | Tổng dung lượng file trong đường dẫn được chọn |
| `pvs` / `vgs` / `lvs` | Xem lần lượt PV, VG và LV của LVM |
| `cat /etc/fstab` | Đọc cấu hình mount bền vững |

## Thay đổi trạng thái — chỉ dùng trong lab đã xác nhận

| Nhóm lệnh | Tác động |
|---|---|
| `mount`, `umount` | Gắn/tháo filesystem trong cây thư mục |
| `fdisk`, `gdisk`, `parted` | Thay đổi partition table |
| `mkfs.*`, `mkswap` | Tạo filesystem hoặc swap; có thể phá dữ liệu cũ trên target |
| Lệnh `pv*`, `vg*`, `lv*` | Tạo hoặc thay đổi cấu trúc LVM; cần biết chính xác target và trạng thái |
| `fsck`, `e2fsck`, `xfs_repair` | Kiểm tra/sửa filesystem; quy trình phụ thuộc loại filesystem và trạng thái mount |

### Quy tắc trước lệnh thay đổi

1. Xác minh tên device, UUID, filesystem type và mount point bằng lệnh quan sát.
2. Xác nhận target thuộc VM/disk lab, không phải disk hệ điều hành hay dữ liệu dùng chung.
3. Ghi lại trạng thái ban đầu và xác nhận có backup/restore phù hợp.
4. Chỉ thay đổi một lớp mỗi lần rồi kiểm tra lại bằng `lsblk`, `findmnt`, `df`.

