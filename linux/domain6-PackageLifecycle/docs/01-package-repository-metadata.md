# Bài 1 — Package, repository và metadata

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

## Nguồn

- [LPIC-1 102.4/102.5 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

