# Bài 5 — `/proc`, `/sys` và `/dev`

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Phân biệt `/proc` (process + kernel), `/sys` (device/kernel objects), `/dev` (device nodes).
> - Biết vì sao chúng trông như file mà không phải dữ liệu trên disk, và vì sao lab **chỉ đọc**.
>
> **Hình dung:** đây là các "bảng điều khiển" kernel dán lên cây thư mục — đọc để xem đồng hồ đo, ghi là vặn núm.


> **Nền tảng + mở rộng:** các đường dẫn này thuộc cây thư mục quen thuộc của Linux và hữu ích khi tìm evidence. Cách dùng sâu các pseudo-filesystem/kernel interface vượt ngoài trọng tâm LPIC 104.6/104.7.

## Vì sao chúng trông như file nhưng không giống file thường?

VFS cho phép chương trình dùng giao diện file/path thống nhất. Nhưng nội dung ở đây thường được kernel tạo động hoặc ánh xạ tới trạng thái kernel/device, không phải dữ liệu thông thường được lưu như file cấu hình trên disk.

| Path | Hệ thống cung cấp | Ví dụ |
|---|---|---|
| `/proc` | thông tin process và kernel; một số runtime tunables | `/proc/self/status`, `/proc/cmdline`, `/proc/sys/` |
| `/sys` | đối tượng thiết bị/kernel và thuộc tính của chúng | `/sys/class/net/`, `/sys/block/` |
| `/dev` | device nodes để chương trình giao tiếp với thiết bị/driver | `/dev/null`, `/dev/zero`, `/dev/sda` |

## `/proc`

`/proc/PID` cho biết thông tin về process; ví dụ `/proc/self` trỏ đến process đang đọc nó. `/proc/sys` chứa một số tham số kernel; việc ghi vào đây có thể đổi cấu hình runtime. Trong lab này chỉ đọc, không ghi.

## `/sys`

`sysfs` trình bày cây đối tượng thiết bị/kernel. Một số thuộc tính có thể ghi và khi ghi có thể làm thay đổi trạng thái thiết bị hoặc kernel. Chỉ đọc trong bài tập.

## `/dev`

Device node là điểm truy cập do kernel/device manager quản lý. `stat` hiển thị loại file và major/minor number cho character/block device. `/dev/null` là thiết bị đặc biệt, không phải file log hay file disk thông thường.

~~~bash
stat /dev/null
stat /dev/zero
~~~

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "File trong `/proc` chiếm dung lượng disk." | Kernel tạo nội dung động khi đọc; size thường hiện 0. |
| "Ghi thử vào `/proc/sys` không sao." | Đổi cấu hình kernel runtime ngay lập tức. |
| "`/dev/null` là file rỗng." | Là character device bỏ mọi dữ liệu ghi vào. |

## Tự kiểm tra

1. Xem dòng lệnh khởi động của PID 1 ở đâu?
2. Tìm danh sách interface mạng qua `/sys` ở đâu?
3. `stat /dev/sda` cho biết loại file gì?

<details>
<summary>Đáp án</summary>

1. `/proc/1/cmdline` (dùng `tr '\0' ' ' < /proc/1/cmdline`).
2. `/sys/class/net/`.
3. Block special file, có major/minor number.

</details>

## Nguồn

- [Linux kernel documentation — `/proc`](https://docs.kernel.org/filesystems/proc.html)
- [Linux kernel documentation — `sysfs`](https://docs.kernel.org/filesystems/sysfs.html)
- [LPI LPIC-1 Objectives V5.0 — FHS 104.7](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

