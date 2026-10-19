# Bài 2 — UUID, mount point và mount/unmount

> **LPIC-1:** phần chính thuộc Objective 104.3. UUID và label được dùng để nhận diện filesystem khi mount.

## Mount là gì?

Linux trình bày filesystem như một cây thư mục thống nhất, bắt đầu ở `/`. **Mount** là gắn một filesystem vào một thư mục trong cây đó; thư mục được chọn gọi là **mount point**.

Ví dụ: khi filesystem của `/dev/sdb1` được mount tại `/data`, người dùng truy cập nội dung filesystem qua `/data/...`. Mount không copy nội dung vào `/data`; nó kết nối filesystem với vị trí đó.

Nếu mount filesystem lên thư mục vốn đã có file, nội dung cũ ở thư mục đó bị **che khuất** trong lúc mount còn hoạt động. Nó không bị xóa; sau khi unmount, nội dung cũ xuất hiện lại. Vì thế cần kiểm tra mount point và thiết bị trước khi ghi dữ liệu.

## UUID khác tên thiết bị

- `/dev/sdb1` là tên đường dẫn thiết bị hiện tại; thứ tự nhận diện disk có thể thay đổi.
- **UUID** định danh filesystem.
- **PARTUUID** định danh partition table entry; nó không đồng nghĩa với UUID của filesystem.
- **Label** là tên dễ đọc do người quản trị đặt cho filesystem.

Để cấu hình mount bền vững, UUID hoặc label thường đáng tin cậy hơn việc dựa vào `/dev/sdX`.

## Mount và unmount

Mount thủ công thường gắn filesystem cho phiên chạy hiện tại. Unmount tháo filesystem khỏi cây thư mục; trước khi tháo, process không được còn sử dụng file ở filesystem đó. Nếu báo “busy”, cần tìm process đang sử dụng, không nên cố ép unmount một cách mù quáng.

Khi một thiết bị không mount như mong đợi, hãy kiểm tra cả hai phía: filesystem thực sự nằm trên thiết bị nào và thiết bị hiện được gắn ở mount point nào. `lsblk -f` và `findmnt` bổ sung cho nhau.

## Nguồn

- [LPIC-1 104.3 — Control mounting and unmounting](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- Tham khảo lệnh: `man mount`, `man umount`, `man findmnt`, `man blkid`.

