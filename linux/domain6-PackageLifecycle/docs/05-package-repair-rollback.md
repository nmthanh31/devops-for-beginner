# Bài 5 — Lỗi, repair và rollback package

## Package có thể lỗi ở đâu?

Một transaction package có thể bị lỗi do:

- Mất điện hoặc bị dừng giữa chừng.
- Dependency không thỏa mãn.
- Repository không truy cập được.
- Hết dung lượng filesystem.
- File cấu hình không hợp lệ.
- Package đang ở trạng thái chưa cấu hình.

## Phân biệt các lớp lỗi

```text
Không tải được package     → repository/network
Cài không được              → package/dependency/disk
Cài xong nhưng không chạy   → config/library/permission
Service không active        → systemd/process/runtime
```

Không nên thấy service không chạy rồi lập tức cài lại package. Trước hết cần kiểm tra package status, dependency, config, status và journal.

## Repair package

Trên Debian/Ubuntu, có các nhóm thao tác để:

- Kiểm tra package cài chưa hoàn tất.
- Cấu hình các package còn dang dở.
- Sửa dependency bị thiếu.

Các lệnh repair có thể thay đổi trạng thái hệ thống, vì vậy phải đọc output và hiểu package nào sẽ bị thay đổi trước khi xác nhận.

## Rollback là gì?

Rollback đưa package về version trước. Rollback không phải lúc nào cũng khả dụng tự động. Cần có ít nhất một trong các nguồn sau:

- Version cũ còn trong repository.
- File package cũ đã lưu.
- Package còn trong cache.
- Snapshot hoặc backup của hệ thống.

Rollback package cũng không tự rollback dữ liệu ứng dụng hoặc database. Vì vậy rollback phần mềm và restore dữ liệu là hai việc khác nhau.

## Nguồn

- [LPIC-1 102.4/102.5 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

