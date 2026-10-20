# Bài 2 — APT và dependency

## APT là gì?

APT là lớp quản lý package cấp cao trên Debian/Ubuntu. Nó làm việc với repository, tính dependency, tải package và gọi `dpkg` để cài đặt.

```text
apt → dpkg → filesystem
```

## Dependency là gì?

Một chương trình có thể cần các package khác để chạy:

```text
app-a
├── lib-x
├── lib-y
└── config-z
```

`app-a` là package chính; các package còn lại là dependency. Nếu dependency thiếu, executable chính có thể tồn tại nhưng chương trình vẫn không chạy được.

## `apt update` và `apt upgrade`

```text
apt update   = tải lại danh sách package
apt upgrade  = cập nhật package đã cài
```

`apt update` không thay đổi version của chương trình đang chạy. Nó chỉ cập nhật thông tin để APT biết version mới nào có trong repository.

`apt upgrade` mới thực hiện việc nâng cấp các package phù hợp.

## Vì sao APT hữu ích hơn cài file thủ công?

Khi cài package từ repository, APT có thể:

1. Tìm package.
2. Tính dependency.
3. Tải đúng package.
4. Cài theo thứ tự phù hợp.
5. Gọi công cụ cấu hình package.

## Nguồn

- [LPIC-1 102.4 — Debian package management](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

