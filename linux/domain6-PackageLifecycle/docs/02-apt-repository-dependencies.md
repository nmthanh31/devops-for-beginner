# Bài 2 — APT và dependency

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Đọc dependency và biết APT giải quyết chúng ra sao.
> - Phân biệt `apt update`, `apt upgrade`, `apt full-upgrade`.
> - Luôn **đọc kế hoạch thay đổi** trước khi gõ `Y`.


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

<!-- learn:tail -->
## Bảng lệnh

| Lệnh | Làm gì | Có thể gỡ package? |
|---|---|---|
| `apt update` | Tải index | Không |
| `apt upgrade` | Nâng cấp, không gỡ gì | Không |
| `apt full-upgrade` | Nâng cấp, cho phép thêm/gỡ để giải dependency | **Có** |
| `apt install -s PKG` | **Mô phỏng** (simulate) | — chỉ in kế hoạch |

## Tự kiểm tra

1. Cách xem APT sẽ làm gì mà không thay đổi hệ thống?
2. Vì sao `full-upgrade` cần đọc kỹ hơn `upgrade`?

<details>
<summary>Đáp án</summary>

1. `apt install -s PKG` / `apt-get -s upgrade`.
2. Nó có thể **gỡ** package để giải dependency.

</details>

## Nguồn

- [LPIC-1 102.4 — Debian package management](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

