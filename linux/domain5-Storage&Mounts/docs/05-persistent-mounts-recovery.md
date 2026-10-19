# Bài 5 — Mount bền vững, kiểm tra và phục hồi

> **LPIC-1:** Objective 104.3 bao gồm cấu hình mount lúc boot, UUID/label và nhận biết systemd mount units. Các quy trình phục hồi dưới đây là hướng vận hành an toàn.

## Vì sao cần mount bền vững?

Mount thủ công thường chỉ tồn tại đến khi unmount hoặc reboot. Để filesystem tự xuất hiện sau boot, Linux thường dùng `/etc/fstab`; systemd có thể tạo mount units tương ứng từ cấu hình này.

Ví dụ minh họa một entry:

```fstab
UUID=<filesystem-uuid>  /data  ext4  defaults  0  2
```

Các trường có thứ tự: thiết bị/UUID, mount point, filesystem type, options, dump flag, fsck pass. Ví dụ chỉ minh họa cấu trúc; UUID, loại filesystem và options phải khớp với thiết bị thật.

## Kiểm tra trước khi reboot

Lỗi trong `/etc/fstab` có thể làm boot bị chậm hoặc thất bại khi filesystem quan trọng không mount được. Quy trình an toàn là:

1. Ghi lại thiết bị, UUID, filesystem type và mount point mong muốn.
2. Đọc cấu hình `fstab` và so sánh từng trường.
3. Dùng công cụ kiểm tra cấu hình và thử mount trong phiên hiện tại.
4. Xác nhận bằng `findmnt` và `df`.
5. Chỉ reboot nếu đó là VM lab có thể khôi phục và việc reboot được cho phép.

`nofail` có thể cho phép boot tiếp khi một filesystem không mount được, nhưng cũng có thể khiến dịch vụ chạy mà thiếu dữ liệu mong đợi. Không thêm tùy chọn này chỉ để che lỗi; phải hiểu tác động tới ứng dụng.

## Chẩn đoán mount sai

- `lsblk -f`: thiết bị/partition, filesystem, UUID, mount point.
- `findmnt`: nguồn nào đang được mount tại đường dẫn nào.
- `df -h` và `df -i`: filesystem đang dùng ở mount point đó và còn bytes/inode hay không.

Nếu mount nhầm vào thư mục đang có dữ liệu, dữ liệu nền bị che trong lúc mount. Hãy xác nhận nguồn và mount point trước khi unmount; đừng xóa file trong thư mục đó để “dọn lỗi” vì có thể đang thao tác trên filesystem khác với dự kiến.

## Chẩn đoán filesystem đầy

1. Dùng `df -h` xác định filesystem nào hết bytes.
2. Dùng `df -i` xem có hết inode không.
3. Dùng `findmnt` xác nhận mount point và source.
4. Tìm nguyên nhân phù hợp, chẳng hạn dữ liệu tăng nhanh hoặc file đã unlink nhưng process còn mở.
5. Nếu cần thay đổi dung lượng, lần theo đúng các lớp block/partition/LVM/filesystem và có kế hoạch restore.

`df` hiển thị triệu chứng ở cấp filesystem; nó chưa tự giải thích thư mục hay process nào gây ra vấn đề.

## Nguồn

- [LPIC-1 104.3 — Control mounting and unmounting](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- Tham khảo lệnh: `man fstab`, `man mount`, `man findmnt`, `man systemd.mount`.

