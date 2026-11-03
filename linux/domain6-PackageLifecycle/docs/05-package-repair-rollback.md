# Bài 5 — Lỗi, repair và rollback package

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Khoanh vùng lỗi package: repo/metadata, dependency, dpkg database, file/config, service.
> - Repair bằng `apt -f install`, `dpkg --configure -a`.
> - Pin và rollback version có kiểm soát.


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

<!-- learn:tail -->
## Pin và rollback — thao tác mẫu

```bash
apt-cache policy PKG                   # các version có sẵn + priority
apt list --installed PKG
sudo apt-mark hold PKG                 # giữ version hiện tại (không upgrade)
apt-mark showhold
sudo apt install PKG=<VERSION_CŨ>      # rollback nếu version cũ còn trên repo/cache
sudo apt-mark unhold PKG
```

Pin theo nguồn/version bằng file trong `/etc/apt/preferences.d/` (Pin-Priority). Rollback chỉ khả thi khi version cũ **còn tải được** (repo, `/var/cache/apt/archives/`, artifact riêng) — hãy kiểm trước khi cần.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Rollback package là trả lại trạng thái cũ." | Config/data/schema có thể đã đổi (L12). |
| "Xóa file trong `/var/lib/dpkg` để sửa lỗi lock." | Tìm process đang giữ lock; không xóa database. |

## Tự kiểm tra

1. `apt upgrade` bị ngắt giữa chừng, giờ mọi lệnh apt báo cần `dpkg --configure -a`. Làm gì?
2. Cách ngăn một package bị nâng cấp trong `apt upgrade` tiếp theo?

<details>
<summary>Đáp án</summary>

1. Chạy `sudo dpkg --configure -a`, rồi `sudo apt -f install`; đọc lỗi nếu còn.
2. `sudo apt-mark hold PKG` (hoặc pin trong `preferences.d`).

</details>

## Nguồn

- [LPIC-1 102.4/102.5 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

