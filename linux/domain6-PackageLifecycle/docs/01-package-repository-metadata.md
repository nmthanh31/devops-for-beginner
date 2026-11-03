# Bài 1 — Package, repository và metadata

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Giải thích package gồm gì (file + metadata + script), repository là gì, metadata dùng để làm gì.
> - Biết vì sao `apt update` không cài gì cả.
>
> **Hình dung:** repository là siêu thị, package là sản phẩm đóng hộp có nhãn (metadata: tên, version, phụ thuộc, chữ ký). `apt update` là lấy **catalog mới** của siêu thị — chưa mua gì.


## Package là gì?

Package là phần mềm đã được đóng gói theo format mà hệ điều hành có thể quản lý. Một package có thể chứa:

- File thực thi.
- File cấu hình.
- Shared library.
- Service unit.
- Documentation.
- Metadata và dependency.

Ví dụ package Debian có đuôi `.deb`; package RPM có đuôi `.rpm`.

Package khác source code. Source code là mã nguồn; package thường là sản phẩm đã build sẵn để cài đặt.

## Repository là gì?

Repository là kho chứa package và các file metadata để package manager biết package nào có sẵn, version nào, dependency nào và tải package từ đâu.

Trên Ubuntu/Debian, cấu hình repository thường nằm ở:

```text
/etc/apt/sources.list
/etc/apt/sources.list.d/
```

Khi chạy `apt update`, hệ thống tải lại **danh sách package** từ repository. Lệnh này chưa tự cập nhật phần mềm đã cài.

## Metadata là gì?

Metadata mô tả package, thường gồm:

- Tên và version.
- Kiến trúc CPU.
- Mô tả.
- Dependency.
- Repository/source.
- Trạng thái cài đặt.
- Checksum hoặc chữ ký tùy hệ thống.

Khi troubleshoot, không chỉ hỏi “package đã cài chưa?”. Cần hỏi thêm “đúng version chưa, dependency có đủ không, package chứa file nào?”.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`apt update` nâng cấp phần mềm." | Chỉ tải metadata/index mới. |
| "Package chỉ là file binary." | Còn config, dependency, maintainer script, chữ ký. |
| "Repo nào cũng tin được." | Chữ ký/key quyết định độ tin cậy; repo lạ là rủi ro supply chain. |

## Tự kiểm tra

1. `apt install foo` báo `Unable to locate package` trên VM mới. Bước đầu tiên nên thử?
2. Metadata repo cũ thì hậu quả gì?

<details>
<summary>Đáp án</summary>

1. `sudo apt update` (index chưa có/cũ), rồi `apt-cache policy foo`.
2. APT không thấy version mới, hoặc cố tải file đã bị xóa khỏi mirror (404).

</details>

## Nguồn

- [LPIC-1 102.4/102.5 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

