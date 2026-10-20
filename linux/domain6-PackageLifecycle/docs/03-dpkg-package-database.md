# Bài 3 — DPKG và package database

## DPKG là gì?

`dpkg` là công cụ cấp thấp của Debian. Nó làm việc trực tiếp với package `.deb` và database package trên máy.

APT thường dùng DPKG ở phía dưới:

```text
apt giải quyết repository/dependency
        ↓
dpkg cài file và ghi trạng thái package
```

## DPKG biết những gì?

DPKG có thể cho biết:

- Package có được cài không.
- Package đang ở version nào.
- Package đã cài những file nào.
- File nào thuộc package nào.
- Package đang ở trạng thái hoàn tất hay chưa cấu hình.

## Tư duy kiểm tra file và package

Khi thấy một file:

```text
File này thuộc package nào?
```

Khi biết một package:

```text
Package này đã cài những file nào?
```

Đây là hai hướng tra cứu khác nhau, tương ứng với việc tìm package từ file và tìm file từ package.

## DPKG không thay thế APT

DPKG không tự giải quyết đầy đủ dependency từ repository. Vì vậy, cài một file `.deb` bằng DPKG có thể thất bại nếu dependency chưa có.

```text
dpkg = quản lý package cục bộ
apt   = repository + dependency + workflow cài đặt
```

## Nguồn

- [LPIC-1 102.4 — Debian package management](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

