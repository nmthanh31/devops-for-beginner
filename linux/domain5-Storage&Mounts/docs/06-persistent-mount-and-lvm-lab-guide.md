# Bài thực hành — Persistent mount và LVM

> Mục tiêu: hiểu một filesystem được mount thế nào, làm sao để mount point tồn tại sau reboot, và LVM thêm những lớp nào trước filesystem.

## Cảnh báo an toàn — đọc trước khi chạy lệnh

Các lệnh `pvcreate`, `mkfs`, `fdisk`, `parted` và một số lệnh LVM thay đổi metadata hoặc filesystem, có thể làm dữ liệu trên thiết bị mất khả năng truy cập. **Chỉ dùng disk trống được cấp riêng cho VM lab. Không dùng disk hệ điều hành, disk đang mount hoặc thiết bị chưa xác định rõ.**

Các placeholder như `<LAB_DISK>` và `<FILESYSTEM_UUID>` không phải cú pháp chạy nguyên văn. Hãy thay bằng giá trị thật sau khi kiểm tra; đừng đoán rằng disk của bạn nhất định là `/dev/sdb`.

---

## Phần A — Mount một filesystem bền vững

Ở phần này cần một filesystem lab đã tồn tại, ví dụ ext4 trên một partition riêng. Nếu chưa có filesystem an toàn để dùng, dừng ở bước kiểm tra; đừng chạy `mkfs` trên disk chưa xác minh.

### 1. Xác định filesystem và trạng thái hiện tại

```bash
lsblk -f
sudo blkid
findmnt
```

- `lsblk -f`: ánh xạ disk/partition sang filesystem, UUID và mount point.
- `blkid`: đọc UUID và filesystem type trực tiếp từ thiết bị.
- `findmnt`: xem các mount hiện có.

Chọn đúng filesystem lab, ghi lại UUID và filesystem type. Xác nhận nó không phải root filesystem (`/`) hay một thiết bị đang chứa dữ liệu cần giữ.

### 2. Tạo mount point riêng

Ví dụ dùng `/srv/labdata`:

```bash
sudo mkdir -p /srv/labdata
```

`mkdir -p` tạo thư mục và các parent còn thiếu; nếu thư mục đã có thì không báo lỗi. Trước khi mount, kiểm tra thư mục này không chứa dữ liệu cần giữ vì nội dung bên dưới sẽ bị che khi mount.

### 3. Lưu bản sao `fstab` rồi thêm cấu hình

Tạo bản sao có timestamp để tránh ghi đè bản backup cũ:

```bash
sudo cp -a /etc/fstab "/etc/fstab.$(date +%F-%H%M%S).bak"
```

Mở file:

```bash
sudoedit /etc/fstab
```

Thêm một dòng với UUID và loại filesystem thực tế của lab:

```fstab
UUID=<FILESYSTEM_UUID>  /srv/labdata  ext4  defaults  0  2
```

Thay `<FILESYSTEM_UUID>` bằng UUID vừa xác nhận; thay `ext4` nếu filesystem thật dùng loại khác. Không thêm một entry trùng cho cùng filesystem/mount point.

Ý nghĩa sáu trường:

1. Thiết bị — ở đây là UUID của filesystem.
2. Mount point.
3. Filesystem type.
4. Mount options.
5. Dump flag — thường `0`.
6. Thứ tự filesystem check lúc boot — thường `2` cho filesystem dữ liệu phù hợp.

### 4. Kiểm tra cấu hình rồi mount

```bash
sudo findmnt --verify --verbose
sudo mount /srv/labdata
findmnt --mountpoint /srv/labdata
df -h /srv/labdata
```

`findmnt --verify` kiểm tra các khai báo mount. `mount /srv/labdata` yêu cầu mount theo entry tương ứng trong `/etc/fstab`. Hai lệnh cuối xác nhận mount source và dung lượng filesystem đang phục vụ đường dẫn.

Nếu có lỗi, không reboot. Đọc thông báo, sửa đúng dòng `fstab`, chạy lại bước kiểm tra rồi mount lại.

### 5. Chứng minh cấu hình có thể mount lại

Chỉ làm bước này nếu filesystem là disk lab riêng, không có process/dịch vụ đang dùng nó:

```bash
sudo umount /srv/labdata
sudo mount /srv/labdata
findmnt --mountpoint /srv/labdata
```

Đây là kiểm tra mount lại từ `fstab`, không phải thử reboot. Chỉ reboot VM disposable khi cần chứng minh boot-time mount và đã xác nhận khả năng phục hồi.

### Rollback phần A

Xóa riêng entry `/srv/labdata` mà bạn vừa thêm vào `/etc/fstab`, kiểm tra `sudo findmnt --verify --verbose`, rồi tháo filesystem nếu không còn được dùng. Không chép đè toàn bộ backup cũ lên `fstab` nếu sau khi backup đã có chỉnh sửa khác.

---

## Phần B — Tạo LVM trên disk lab mới, rồi mount bền vững

### 1. Xác nhận disk trống và riêng cho lab

```bash
lsblk -f
sudo pvs
sudo vgs
sudo lvs
```

Phải biết chính xác disk nào được cấp cho bài lab, ví dụ placeholder `/dev/<LAB_DISK>`. Không chọn disk có mount point, filesystem/data cần giữ, hoặc disk chứa `/` hay `/boot`. Nếu không thể xác định chắc chắn, dừng và hỏi trước khi thay đổi.

### 2. Tạo các lớp LVM

Thay `<LAB_DISK>` bằng whole disk lab đã xác minh. Các lệnh sau là **lệnh thay đổi trạng thái**:

```bash
sudo pvcreate /dev/<LAB_DISK>
sudo vgcreate vg_lab /dev/<LAB_DISK>
sudo lvcreate -L 2G -n lv_data vg_lab
```

- `pvcreate`: khởi tạo disk làm LVM Physical Volume (PV).
- `vgcreate`: tạo Volume Group (VG) tên `vg_lab` từ PV.
- `lvcreate -L 2G -n lv_data`: cấp 2 GiB từ VG để tạo Logical Volume (LV) tên `lv_data`.

Sau đó đọc lại trạng thái:

```bash
sudo pvs
sudo vgs
sudo lvs
lsblk -f
```

Mô hình lúc này:

```text
disk lab → PV → VG vg_lab → LV lv_data
```

### 3. Tạo filesystem trên LV mới

Chỉ format LV vừa tạo và vừa xác minh:

```bash
sudo mkfs.ext4 /dev/vg_lab/lv_data
```

`mkfs.ext4` tạo filesystem ext4 trên LV; nếu chạy nhầm target, dữ liệu target có thể bị phá hủy. Lấy UUID sau khi tạo:

```bash
sudo blkid /dev/vg_lab/lv_data
```

### 4. Mount LV và cấu hình persistent

Tạo mount point:

```bash
sudo mkdir -p /srv/lvm-lab
```

Sao lưu `/etc/fstab` theo cách ở Phần A, rồi thêm entry dùng UUID vừa lấy:

```fstab
UUID=<LV_FILESYSTEM_UUID>  /srv/lvm-lab  ext4  defaults  0  2
```

Kiểm tra và mount:

```bash
sudo findmnt --verify --verbose
sudo mount /srv/lvm-lab
findmnt --mountpoint /srv/lvm-lab
df -h /srv/lvm-lab
```

Filesystem được tạo trên LV; chính filesystem đó được mount vào `/srv/lvm-lab`. Ứng dụng truy cập dữ liệu bằng đường dẫn `/srv/lvm-lab/...`, không cần biết các lớp PV/VG/LV bên dưới.

### 5. Thực hành mở rộng LV — chỉ nếu VG còn dung lượng trống

Xem `VFree` trong `sudo vgs` trước. Nếu lab có đủ free extents và bạn được yêu cầu mở rộng, `-r` yêu cầu LVM thử resize filesystem cùng LV:

```bash
sudo lvextend -L +1G -r /dev/vg_lab/lv_data
```

`+1G` nghĩa là tăng thêm 1 GiB, không phải đặt tổng kích thước thành 1 GiB. Sau đó xác minh bằng:

```bash
sudo lvs
df -h /srv/lvm-lab
```

Không chạy lệnh này nếu VG không còn đủ dung lượng hoặc filesystem/thiết bị thực tế khác ví dụ. Cách mở rộng phụ thuộc filesystem và tình trạng storage.

---

## Kết quả cần giải thích bằng lời

- `lsblk -f`: disk/partition/LV nào chứa filesystem nào?
- `pvs`, `vgs`, `lvs`: dung lượng nằm ở lớp LVM nào?
- `findmnt`: filesystem nào đang phục vụ mount point?
- `df -h`: filesystem còn bao nhiêu dung lượng bytes?
- Vì sao `/etc/fstab` dùng UUID và làm sao kiểm tra entry trước khi reboot?

## Nguồn

- [LPIC-1 Objectives V5.0 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0): 102.1, 104.1, 104.2, 104.3.
- LVM chi tiết hơn phần yêu cầu cơ bản của LPIC-1 được ghi là phần thực hành/mở rộng của roadmap.

