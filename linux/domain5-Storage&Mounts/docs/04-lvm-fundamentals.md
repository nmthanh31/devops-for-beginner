# Bài 4 — LVM: PV, VG và LV

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Giải thích PV → VG → LV và vì sao LVM linh hoạt hơn partition cố định.
> - Biết mở rộng dung lượng là **chuỗi nhiều lớp** (LV rồi filesystem).
>
> **Hình dung:** PV là từng thùng nước, VG là bể chung đổ tất cả thùng vào, LV là các vòi lấy nước ra từ bể với dung tích tùy chỉnh. Filesystem là cái bình hứng ở mỗi vòi — nới vòi rộng ra vẫn phải nới bình.


> **LPIC-1:** LVM được nhắc ở mức tính năng cơ bản trong Objective 102.1 (thiết kế disk layout). Roadmap lab có thể đi sâu hơn phần LPIC yêu cầu.

## Vì sao có LVM?

Nếu filesystem nằm trực tiếp trên một partition cố định, việc đổi cách phân chia dung lượng có thể khó. LVM thêm một lớp quản lý dung lượng logic để có thể gom và cấp dung lượng linh hoạt hơn.

```text
Disk/partition → PV → VG → LV → filesystem → mount point
```

### PV — Physical Volume

PV là disk hoặc partition đã được đưa vào LVM để làm nguồn cung cấp dung lượng.

### VG — Volume Group

VG là nhóm dung lượng được tổng hợp từ một hoặc nhiều PV. Có thể hình dung VG như một kho dung lượng.

### LV — Logical Volume

LV là phần dung lượng được cấp ra từ VG. Filesystem thường được tạo trên LV, rồi filesystem đó được mount vào cây thư mục.

## Mở rộng dung lượng là chuỗi nhiều lớp

LVM không làm cho disk vật lý tự lớn lên. Nếu cần thêm dung lượng, phải có dung lượng mới ở lớp dưới rồi cập nhật các lớp liên quan phía trên. Tùy tình huống có thể cần mở rộng disk ảo, partition/PV, VG, LV và cuối cùng filesystem.

Không phải mọi thao tác đều cần đủ tất cả các lớp; trước khi làm phải xác định chính xác hiện trạng. Filesystem và LVM có công cụ/quy trình riêng, nên không được đoán lệnh chỉ từ một dòng `df`.

## LVM không phải backup

LVM giúp quản lý cấp phát dung lượng. Nó không tự bảo vệ khỏi xóa nhầm, hỏng filesystem, mất disk hoặc lỗi thao tác. Snapshot có thể hỗ trợ một số workflow nhất định nhưng không thay thế bản backup có thể restore.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`lvextend` xong là `df` tăng." | Phải resize filesystem (`-r` hoặc `resize2fs`/`xfs_growfs`). |
| "LVM snapshot là backup." | Cùng PV/VG; mất disk là mất cả hai (xem [L12](../../domain12-BackupRecovery/docs/01-backup-design.md)). |
| "`-L 1G` là tăng thêm 1G." | `-L 1G` đặt tổng; `-L +1G` mới là tăng thêm. |

## Tự kiểm tra

1. `vgs` báo `VFree 0`. Muốn mở rộng LV phải làm gì trước?
2. Sau `lvextend -L +5G` (không `-r`), `df -h` không đổi. Vì sao?

<details>
<summary>Đáp án</summary>

1. Thêm PV vào VG (`pvcreate` disk mới → `vgextend`).
2. Mới mở rộng LV; filesystem chưa được resize.

</details>

## Nguồn

- [LPIC-1 102.1 — Design hard disk layout](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- Tài liệu học LPI: [LPIC-1 Learning Material 101](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf)
- Tham khảo lệnh: `man lvm`, `man pvs`, `man vgs`, `man lvs`.

