# Lab 4 — Khám phá `/proc`, `/sys`, `/dev` (read-only)

## Mục tiêu

Nhận diện các pseudo-filesystem và lấy evidence mà không ghi/chỉnh tham số kernel hay thiết bị.

## Bước 1 — Xác nhận mount

~~~bash
findmnt /proc
findmnt /sys
findmnt /dev
~~~

## Bước 2 — Đọc process/kernel interface trong `/proc`

~~~bash
cat /proc/self/status | head -n 12
readlink /proc/self/exe
cat /proc/cmdline
~~~

`self` nói tới process đang thực hiện lệnh. Ghi lại một thông tin process và một thông tin boot/kernel.

## Bước 3 — Quan sát thiết bị trong `/sys`

~~~bash
ls /sys/class
ls /sys/class/net
find /sys/class/net -maxdepth 2 -type l -print
~~~

Chọn một interface mạng và lần theo symlink bằng `readlink -f`. Không ghi giá trị vào bất kỳ file nào dưới `/sys`.

## Bước 4 — Quan sát device node trong `/dev`

~~~bash
stat /dev/null
stat /dev/zero
file /dev/null /dev/zero
~~~

Ghi loại file và major/minor nếu `stat` hiển thị. Giải thích vì sao đây không phải file dữ liệu bình thường.

## Kết luận

Hoàn thành bảng:

| Cây | Vai trò | Evidence đã đọc |
|---|---|---|
| `/proc` | | |
| `/sys` | | |
| `/dev` | | |

