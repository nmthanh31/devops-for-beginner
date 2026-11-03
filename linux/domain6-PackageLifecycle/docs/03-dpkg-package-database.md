# Bài 3 — DPKG và package database

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Dùng `dpkg -s`, `-L`, `-S` để hỏi: package có cài không, gồm file gì, file này của package nào.
> - Hiểu dpkg làm việc cục bộ, APT lo repo + dependency.
>
> **Hình dung:** dpkg là **sổ kho** của máy — biết chính xác món nào đã nhập, nằm ở kệ nào. APT là **bộ phận mua hàng** — đi siêu thị, chọn đúng phiên bản, mua kèm đồ cần thiết.


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

<!-- learn:tail -->
## Ba câu hỏi, ba lệnh

| Câu hỏi | Lệnh |
|---|---|
| Package X đã cài? Version? | `dpkg -s X` |
| Package X cài những file nào? | `dpkg -L X` |
| File `/usr/bin/y` thuộc package nào? | `dpkg -S /usr/bin/y` |
| File của package có bị sửa không? | `dpkg --verify X` (hoặc `debsums`) |

## Tự kiểm tra

1. Thấy file lạ `/etc/foo.conf`, muốn biết package nào mang nó tới?
2. `dpkg -S` không trả kết quả cho một binary trong `/usr/local/bin`. Nghĩa gì?

<details>
<summary>Đáp án</summary>

1. `dpkg -S /etc/foo.conf`.
2. Không do package quản lý (cài tay/script) — dpkg không theo dõi được, phải tự quản lý version/rollback.

</details>

## Nguồn

- [LPIC-1 102.4 — Debian package management](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

