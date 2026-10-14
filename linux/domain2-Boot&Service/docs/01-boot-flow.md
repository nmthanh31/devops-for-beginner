# Bài 1 — Boot Process: từ Firmware đến dịch vụ Linux

> Bài này bám theo phạm vi LPIC-1 101.2 “Boot the system” và nối với runlevel/target của 101.3. Nội dung được diễn giải lại bằng lời dễ học, không sao chép nguyên văn giáo trình.

## Mục tiêu

Sau bài này, bạn có thể:

- kể đúng thứ tự các giai đoạn boot;
- giải thích BIOS khác UEFI ở cách gọi bootloader;
- nói GRUB làm gì và kernel nhận tham số từ đâu;
- giải thích vì sao có initramfs;
- phân biệt kernel với chương trình init đầu tiên;
- nhận diện SysVinit, systemd và Upstart ở mức nền tảng;
- tìm log boot bằng dmesg và journalctl;
- hiểu cách kiểm tra boot time;
- biết cách thử thay đổi boot an toàn trên máy ảo hoặc bản sao cloud image.

LPIC-1 101.2 tập trung vào boot sequence, tham số bootloader/kernel, init systems và kiểm tra boot events. Lab can thiệp image ở cuối bài là phần mở rộng theo đề bài của bạn, không phải yêu cầu cốt lõi của mục tiêu 101.2.

---

## 1. Bức tranh tổng thể

Khi máy đang tắt, CPU chưa chạy Linux, chưa có process và chưa có systemd. Khi bật nguồn, mỗi thành phần làm một phần việc rồi bàn giao cho thành phần tiếp theo:

~~~text
Nguồn bật
   ↓
Firmware (BIOS hoặc UEFI)
   ↓
Bootloader (thường là GRUB)
   ↓
Linux kernel + initramfs
   ↓
root filesystem thật
   ↓
chương trình init đầu tiên (PID 1)
   ↓
services, login, network và ứng dụng
~~~

Mẹo nhớ: **Firmware tìm đường; bootloader chọn và nạp; kernel dựng nền tảng; init khởi chạy userspace.**

“Máy đã lên” có nhiều mốc khác nhau:

~~~text
kernel chạy
≠ root filesystem đã mount
≠ systemd đã đạt target
≠ SSH đã nhận kết nối
≠ ứng dụng đã sẵn sàng phục vụ
~~~

---

## 2. Firmware: BIOS và UEFI

Firmware là phần mềm nền tảng được lưu trên bo mạch chủ. Nó chạy trước Linux.

### 2.1. BIOS kiểu cũ

Luồng khái niệm trên máy x86 dùng BIOS:

1. Khi bật nguồn, firmware thực hiện POST — kiểm tra phần cứng ở mức cơ bản.
2. BIOS chọn thiết bị boot theo thứ tự đã cấu hình.
3. BIOS đọc mã boot đầu tiên trên thiết bị đó.
4. Mã bootloader tiếp tục tìm phần còn lại của GRUB, hiển thị menu nếu cần, rồi nạp kernel.

Trong cách phân vùng MBR cổ điển, sector đầu tiên có 512 byte, gồm vùng mã khởi động, bảng phân vùng và chữ ký. Tài liệu LPIC mô tả giai đoạn đầu BIOS đọc 440 byte đầu tiên. Đây là mô hình học tập cho BIOS/MBR; cách GRUB được cài thực tế có thể có thêm giai đoạn và vùng chứa mã, nên không nên suy ra rằng toàn bộ GRUB luôn nằm gọn trong đúng 440 byte.

### 2.2. UEFI hiện đại

UEFI cũng là firmware, nhưng có thể đọc EFI System Partition (ESP) và chạy một tệp EFI application.

Luồng khái niệm:

1. Firmware kiểm tra và khởi tạo phần cứng.
2. Firmware đọc boot entry lưu trong NVRAM.
3. Boot entry trỏ đến EFI application, thường là bootloader, trên ESP.
4. UEFI chạy application đó; bootloader nạp kernel và initramfs.

Phân biệt:

~~~text
NVRAM: lưu boot entries/thứ tự boot và đường dẫn EFI application
ESP: phân vùng chứa tệp EFI application, thường dùng FAT
~~~

UEFI không lưu chính tệp GRUB bên trong NVRAM; NVRAM thường lưu mục chỉ đường tới tệp trên ESP.

### 2.3. Secure Boot

Secure Boot là cơ chế UEFI kiểm tra chuỗi khởi động theo chính sách chữ ký tin cậy. Tùy cách phân phối Linux, shim và GRUB đã ký có thể tham gia chuỗi này. Không nên diễn đạt đơn giản rằng mọi EFI application đều phải được “nhà sản xuất xác thực”; trust database và cách ký phụ thuộc nền tảng/cấu hình.

### Lab 1 — Xác định máy Linux hiện tại khởi động theo UEFI hay không

Các lệnh sau chỉ đọc:

~~~bash
if [ -d /sys/firmware/efi ]; then
  echo "Booted with UEFI"
else
  echo "UEFI runtime interface not present; likely BIOS/legacy boot"
fi

lsblk -f
findmnt /boot/efi
~~~

Ghi lại:

- Có thư mục /sys/firmware/efi không?
- Có phân vùng FAT được mount tại /boot/efi không?
- Vì sao một máy ảo có thể boot UEFI dù máy host dùng firmware khác?

Không có /sys/firmware/efi thường nghĩa kernel hiện tại không được boot qua UEFI; đừng kết luận chỉ từ tên distro.

---

## 3. Bootloader: GRUB làm gì?

Bootloader là chương trình được firmware gọi để tiếp tục quá trình boot. Trên nhiều Linux x86, bootloader thường gặp là GRUB.

GRUB giúp:

- chọn kernel nếu máy có nhiều kernel;
- chọn recovery entry nếu được tạo;
- nạp kernel và initramfs vào bộ nhớ;
- truyền kernel command line cho kernel.

### 3.1. GRUB menu và cấu hình

Trên Ubuntu, cấu hình thường được quản trị tại:

~~~text
/etc/default/grub
~~~

Các script trong /etc/grub.d/ và cấu hình hệ thống được dùng để tạo file sinh ra, thường là:

~~~text
/boot/grub/grub.cfg
~~~

Không chỉnh trực tiếp grub.cfg như cách quản trị thông thường vì file này được tạo lại. Sau khi sửa cấu hình nguồn, Ubuntu thường dùng:

~~~bash
sudo update-grub
~~~

update-grub tạo lại cấu hình menu; nó không đồng nghĩa đã cài lại bootloader vào MBR hoặc ESP.

Một số hệ thống ẩn menu. Cách hiện menu tạm thời phụ thuộc firmware, distro và cấu hình; phím thường gặp là Esc hoặc Shift, nhưng không có phím duy nhất đúng trên mọi máy.

### 3.2. Kernel command line

Kernel command line là chuỗi tham số bootloader truyền cho kernel. Xem tham số của lần boot hiện tại:

~~~bash
cat /proc/cmdline
~~~

Thường có dạng tên=giá_trị, hoặc một từ khóa đứng riêng.

| Tham số | Ý nghĩa đơn giản | Lưu ý |
|---|---|---|
| root=... | Chỉ định root filesystem | UUID/PARTUUID thường ổn định hơn tên /dev/sdaN; initramfs và distro cũng ảnh hưởng cách tìm root |
| ro | Mount root ban đầu chỉ đọc | Hệ thống thường remount theo cấu hình sau đó |
| rw | Yêu cầu root mount ban đầu đọc/ghi | Chỉ dùng khi biết tác động |
| quiet | Giảm phần lớn thông báo boot | Có thể làm khó chẩn đoán |
| systemd.unit=multi-user.target | Yêu cầu systemd đi tới target này | Thường là chế độ server không GUI |
| systemd.unit=rescue.target | Yêu cầu chế độ rescue | Có thể cần console và xác thực phù hợp |
| init=/bin/bash | Thay init bằng shell | Rất nhạy cảm; bỏ qua phần lớn quản lý hệ thống, chỉ thử trong VM cô lập |
| mem=512M | Giới hạn RAM kernel sử dụng | Hữu ích cho thử nghiệm VM |
| maxcpus=2 | Giới hạn số CPU kernel sử dụng | Hữu ích cho thử nghiệm |
| acpi=off | Tắt hỗ trợ ACPI | Có thể làm hỏng quản lý điện/nhiệt/thiết bị; không dùng như mẹo tối ưu |
| vga=ask | Chọn video mode kiểu cũ | Tham số legacy; không phù hợp với nhiều hệ thống đồ họa/UEFI mới |

LPIC đưa các tham số này làm ví dụ nhận diện. Đó không phải danh sách để thêm tất cả vào máy. Tham số sai có thể khiến máy không boot hoặc mất khả năng quản trị từ xa.

### Lab 2 — Đọc kernel command line

~~~bash
cat /proc/cmdline
~~~

Chọn ba tham số và ghi:

~~~text
tham số:
giá trị:
thành phần có khả năng sử dụng nó:
điều gì có thể xảy ra nếu giá trị sai:
~~~

Đây là bài đọc trạng thái hiện tại; không sửa GRUB trên máy đang dùng.

---

## 4. Kernel, initramfs và root filesystem

### 4.1. Kernel bắt đầu làm việc

Bootloader nạp kernel vào RAM và chuyển quyền điều khiển cho kernel. Kernel bắt đầu thiết lập bộ nhớ, CPU, driver, thiết bị và các cơ chế nền tảng.

Kernel cần tìm và truy cập root filesystem. Nhưng driver hoặc công cụ để đọc ổ đĩa có thể lại nằm bên trong root filesystem chưa truy cập được. Đây là bài toán “cần root để đọc driver, nhưng cần driver mới đọc được root”.

### 4.2. initramfs giải quyết bài toán này

initramfs là archive chứa filesystem ban đầu. Kernel dùng nó làm root tạm thời trong giai đoạn sớm.

initramfs có thể chứa:

- kernel modules cần cho storage/controller;
- công cụ nhận diện filesystem;
- logic mở khóa LUKS;
- công cụ kích hoạt LVM/RAID;
- script hoặc chương trình tìm root filesystem thật.

Luồng hiện đại dễ hình dung:

~~~text
bootloader nạp kernel + initramfs
       ↓
kernel khởi chạy môi trường initramfs
       ↓
initramfs tìm/mở root filesystem thật
       ↓
chuyển root sang filesystem thật (switch_root/pivot_root)
       ↓
chạy init trên hệ thống chính
~~~

Trên nhiều hệ thống, chương trình khởi chạy bên trong initramfs là /init. Sau khi chuyển sang root thật, system manager chính được chạy. Chi tiết thay đổi tùy distro và cấu hình.

Khi không còn cần initramfs làm root ban đầu, hệ thống chuyển sang root thật; vùng nhớ của initramfs có thể được thu hồi. Cách mô tả “initramfs bị xóa hoàn toàn khỏi RAM ngay khi init chạy” là quá đơn giản để áp dụng cho mọi cấu hình.

### 4.3. Vai trò của /etc/fstab

/etc/fstab mô tả nhiều filesystem cần mount trên hệ thống chính. Không nên hiểu rằng kernel tự đọc toàn bộ /etc/fstab trước khi chạy init. Trong hệ thống hiện đại, init/system manager và công cụ userspace thường tham gia xử lý mount theo cấu hình.

### 4.4. Khi nào cần can thiệp initramfs?

Chỉ khi có lý do cụ thể, ví dụ:

- boot không tìm được root vì thiếu storage driver;
- thay đổi LVM, RAID hoặc encryption;
- cần sửa hook/module được nạp ở giai đoạn sớm;
- đang chẩn đoán lỗi initramfs.

Trên Ubuntu, các vị trí thường gặp:

~~~text
/boot/initrd.img-<kernel-version>
/etc/initramfs-tools/modules
/etc/initramfs-tools/conf.d/
/etc/initramfs-tools/hooks/
/etc/initramfs-tools/scripts/
~~~

Các lệnh quan sát/tạo lại thường gặp:

~~~bash
lsinitramfs /boot/initrd.img-$(uname -r)
sudo update-initramfs -u
sudo update-initramfs -u -k all
~~~

Không chạy cập nhật initramfs trên image hoặc máy quan trọng nếu chưa xác nhận đúng root, kernel và bản sao có thể khôi phục.

---

## 5. Init: chương trình đầu tiên và các hệ thống quản lý dịch vụ

Sau khi kernel chuẩn bị userspace, nó chạy chương trình init đầu tiên. Trên hệ thống Linux thông thường, process đầu tiên này có PID 1. PID 1 khởi tạo các dịch vụ và môi trường đăng nhập.

LPI yêu cầu nhận biết ba họ init:

### 5.1. SysVinit

SysVinit dùng runlevel và script dịch vụ. Quy ước thường gặp:

| Runlevel | Ý nghĩa phổ biến |
|---|---|
| 0 | Halt/shutdown |
| 1 hoặc S | Single-user/maintenance |
| 2, 3, 4 | Multi-user; ý nghĩa cụ thể tùy distro |
| 5 | Multi-user có đồ họa trên nhiều distro |
| 6 | Reboot |

Không phải mọi distro đều gán runlevel 2–5 giống nhau.

Các path lịch sử thường gặp:

~~~text
/etc/inittab
/etc/init.d/
/etc/rc0.d/ ... /etc/rc6.d/
~~~

Trong thư mục rcX.d, liên kết bắt đầu bằng S thường biểu thị start, K biểu thị stop khi chuyển runlevel. Đây là mô hình lịch sử; không áp dụng nó như cách quản lý mặc định trên Ubuntu hiện đại dùng systemd.

### 5.2. systemd

systemd là system/service manager phổ biến trên distro hiện đại. Nó dùng units, targets và dependency; có thể chạy jobs song song, quản lý cgroup và hỗ trợ socket activation.

~~~bash
systemctl get-default
systemctl list-units --type=target
systemctl is-system-running
~~~

Target là trạng thái/điểm hội tụ tương ứng ở mức khái niệm với runlevel, không phải process riêng.

| SysV runlevel thường gặp | systemd target thường gặp |
|---|---|
| 0 | poweroff.target |
| 1/S | rescue.target |
| 3 | multi-user.target |
| 5 | graphical.target |
| 6 | reboot.target |

Đây là ánh xạ tương thích phổ biến, không phải định nghĩa cứng cho mọi distro.

### 5.3. Upstart

Upstart là init thay thế lịch sử, từng được dùng trong Ubuntu cũ và hỗ trợ khởi động theo sự kiện/song song. Ubuntu hiện đại đã chuyển sang systemd; ở LPIC cần nhận biết Upstart, không xem nó là lựa chọn vận hành mặc định.

---

## 6. Tham số boot để chẩn đoán

GRUB cho phép sửa kernel command line tạm thời từ menu boot. Trong VM thử nghiệm:

1. mở menu GRUB;
2. chọn entry và vào chế độ edit;
3. sửa dòng bắt đầu bằng linux;
4. boot entry đã sửa một lần.

Thay đổi tạm trong menu thường không sửa file cấu hình trên disk. Cách mở menu và phím boot phụ thuộc VM/firmware.

Ví dụ nhận biết:

- systemd.unit=rescue.target: yêu cầu chế độ rescue.
- systemd.unit=multi-user.target: yêu cầu target nhiều người dùng không GUI.
- quiet: giảm thông báo.
- bỏ quiet: thường giúp xem thông báo boot rõ hơn.

Không thử init=/bin/bash, root=..., acpi=off trên máy thật hoặc cloud instance đang cung cấp dịch vụ. Tham số sai có thể làm mất SSH; khi đó cần console hoặc khôi phục image.

---

## 7. Kiểm tra boot events: dmesg và journalctl

### 7.1. Kernel ring buffer và dmesg

Kernel ghi thông báo vào vùng nhớ dạng vòng gọi là kernel ring buffer. dmesg hiển thị thông báo hiện đang có trong vùng này.

~~~bash
dmesg
dmesg -T
dmesg | less
~~~

Timestamp dạng [ 5.262389 ] thường là thời gian tương đối từ lúc kernel khởi động. dmesg -T thử hiển thị thời gian dễ đọc; phép quy đổi có thể kém chính xác trên một số hệ thống.

Ring buffer hữu ích để xem driver, thiết bị, filesystem và lỗi giai đoạn kernel. Buffer có giới hạn và có thể bị ghi đè; nó không phải kho lịch sử bền vững. Khi máy tắt, buffer mất. dmesg --clear xóa nội dung hiện tại, vì vậy đừng chạy trước khi thu evidence.

### 7.2. Journal trên systemd

~~~bash
journalctl --list-boots
journalctl -b 0
journalctl -b -1
journalctl -k
journalctl -b -k
~~~

- --list-boots: các boot journal đang lưu.
- -b 0: boot hiện tại.
- -b -1: boot trước, nếu còn được lưu.
- -k: chỉ kernel messages.
- -b -k: kernel messages của boot hiện tại.

Journal có thể volatile hoặc persistent tùy cấu hình. Không mặc định rằng mọi boot cũ đều tồn tại.

### 7.3. /var/log và rescue media

Một số hệ thống ghi log text dưới /var/log, ví dụ syslog/messages nếu dịch vụ tương ứng được cài và cấu hình. Journal binary cần đọc bằng journalctl, không đọc trực tiếp bằng cat.

Nếu root filesystem của máy lỗi được mount tại /mnt từ rescue system, thử đọc journal đã lưu:

~~~bash
journalctl --directory=/mnt/var/log/journal --list-boots
~~~

Lệnh chỉ hữu ích nếu journal persistent tồn tại ở đó và rescue environment có phiên bản journalctl tương thích.

### Lab 3 — Tìm boot error gần nhất

Chỉ đọc log:

~~~bash
dmesg -T | less
journalctl -b -p warning..alert --no-pager
journalctl -b -k --no-pager | tail -n 80
~~~

Ghi ba dòng đáng chú ý, thời điểm xuất hiện và lớp liên quan: kernel/driver, mount, service hay application. Đừng sửa gì chỉ dựa trên một warning; tìm thêm context quanh nó.

---

## 8. Đo thời gian boot

~~~bash
systemd-analyze time
systemd-analyze blame
systemd-analyze critical-chain
~~~

- time: tổng quan firmware, loader, kernel, initrd và userspace khi hệ thống cung cấp dữ liệu đó.
- blame: activation duration được systemd ghi nhận cho các unit phù hợp.
- critical-chain: chuỗi timing dependency ảnh hưởng target/unit được hỏi.

blame không tự tìm root cause. Unit có thời gian dài có thể đang chờ event hoặc chạy song song mà không nằm trên đường quyết định thời điểm target đạt được. Đối chiếu critical-chain, log và trạng thái unit.

### Lab 4 — Tìm bottleneck mà không đoán

~~~bash
systemd-analyze time
systemd-analyze blame | head -n 15
systemd-analyze critical-chain multi-user.target
~~~

Chọn unit có thời gian activation cao:

1. Nó có nằm trên critical chain của target bạn quan tâm không?
2. Journal cho biết nó xử lý việc hay đang chờ?
3. Có bằng chứng nào cho thấy tắt unit đó an toàn không?

Không disable service chỉ vì nó đứng đầu blame.

---

## 9. Mở rộng: can thiệp Ubuntu Cloud Image

Đề bài của bạn yêu cầu đọc và chỉnh cloud image Ubuntu 20.04. Đây là phần nâng cao: sai phân vùng, sai root hoặc tháo mount không đúng có thể làm hỏng image hoặc ảnh hưởng host.

### 9.1. Nguyên tắc an toàn

- Giữ file gốc bất biến; tạo bản sao riêng để thử.
- Xác nhận đường dẫn image, định dạng và phân vùng trước khi mount.
- Không chạy cleanup hàng loạt trên image chưa boot thử.
- Không xóa cloud-init khỏi image cloud dùng để tạo VM mới: nó thường thiết lập hostname, mạng, user và SSH key theo metadata/user-data.
- Không disable network wait-online, apt timers, snapd, rsyslog hoặc gỡ package chỉ vì một nguồn nói chúng “không cần”. Đo thời gian và xác nhận chức năng trước.
- Không chạy zero-fill như thao tác mặc định. Ghi file zero đến khi đầy filesystem có thể gây hết dung lượng và lỗi; chỉ thử trên bản sao disposable nếu hiểu rõ mục tiêu.

### 9.2. Kiểm tra image trước khi mount

~~~bash
qemu-img info ubuntu-20.04-copy.qcow2
~~~

Lệnh trên chỉ đọc metadata. Thực hiện bước ghi tiếp theo chỉ với bản sao.

### 9.3. Gắn image QCOW2 để xem filesystem

Các lệnh cần quyền root. Ví dụ giả định nbd0 chưa được dùng. Xác nhận target đúng và không gắn image gốc:

~~~bash
sudo modprobe nbd max_part=8
sudo qemu-nbd --connect=/dev/nbd0 ubuntu-20.04-copy.qcow2
sudo udevadm settle
lsblk -f /dev/nbd0
~~~

Đọc output để xác định root partition và nếu có ESP. Đừng mặc định root luôn p1 hay ESP luôn p15.

Mount đúng phân vùng đã xác định:

~~~bash
sudo mkdir -p /mnt/image
sudo mount /dev/nbd0pX /mnt/image
findmnt -T /mnt/image
lsblk -f /dev/nbd0
~~~

Thay pX bằng phân vùng root đã xác định từ lsblk, không sao chép nguyên placeholder. Nếu có ESP, kiểm tra layout trước rồi mới mount đúng phân vùng đó vào /mnt/image/boot/efi. Image có thể không cần mount ESP riêng cho tác vụ đang làm.

Nếu /boot nằm trên phân vùng riêng, mount phân vùng /boot của image vào /mnt/image/boot trước khi vào chroot; nếu không, update-grub/update-initramfs có thể thao tác nhầm cây filesystem.

### 9.4. Chỉnh GRUB trong image

Để cập nhật cấu hình bên trong chroot, bind mount pseudo-filesystem vào root image:

~~~bash
sudo mount --rbind /dev /mnt/image/dev
sudo mount --make-rslave /mnt/image/dev
sudo mount --rbind /proc /mnt/image/proc
sudo mount --make-rslave /mnt/image/proc
sudo mount --rbind /sys /mnt/image/sys
sudo mount --make-rslave /mnt/image/sys
sudo mount --rbind /run /mnt/image/run
sudo mount --make-rslave /mnt/image/run
~~~

Sau đó vào chroot:

~~~bash
sudo chroot /mnt/image
~~~

Trong chroot, kiểm tra trước:

~~~bash
cat /etc/default/grub
ls /boot
~~~

Sửa nguồn cấu hình /etc/default/grub bằng editor. Ví dụ đổi timeout hoặc bỏ quiet để xem boot messages. Sau đó tạo lại cấu hình:

~~~bash
update-grub
~~~

Nếu thay đổi module/hook initramfs thì cập nhật initramfs phù hợp:

~~~bash
update-initramfs -u -k all
~~~

Không chạy grub-install theo thói quen khi chỉ đổi tham số GRUB. Việc cài bootloader phụ thuộc firmware mode, thiết bị đích và layout; chọn sai có thể làm image không boot.

### 9.5. Thoát và tháo image sạch

Thoát chroot:

~~~bash
exit
~~~

Unmount các bind mount và filesystem image theo thứ tự ngược. Trước khi tháo, kiểm tra không có process đang dùng:

~~~bash
findmnt -R /mnt/image
sudo umount -R /mnt/image
sudo qemu-nbd --disconnect /dev/nbd0
~~~

Nếu unmount báo busy, tìm process giữ mount và xử lý; không ngắt NBD đang được sử dụng.

### 9.6. Boot thử và so sánh

Boot bản sao trong QEMU/KVM với firmware mode phù hợp. Ghi baseline và kết quả:

- image gốc và image chỉnh sửa;
- firmware mode;
- kernel command line;
- thời gian boot;
- lỗi trong console, dmesg và journal;
- SSH/network/application có hoạt động không.

Chỉ so sánh công bằng khi môi trường ảo hóa và tài nguyên VM giống nhau.

### Đánh giá việc tối ưu image

Xóa package/service có trade-off. Cloud-init thường cần cho cloud workflow; OpenSSH có thể là đường quản trị duy nhất; network manager và wait-online ảnh hưởng service phụ thuộc mạng; unattended-upgrades liên quan bảo mật; snapd/rsyslog có thể là dependency hoặc yêu cầu vận hành.

Quy trình sysadmin:

~~~text
đo baseline → xác định unit gây chờ → xem journal/dependency
→ thay đổi một thứ → boot test → kiểm tra chức năng
→ so sánh lại → giữ hoặc rollback
~~~

QCOW2 có virtual size khác disk size thực tế. qemu-img convert tạo file image mới; kiểm tra output và boot thử trước khi thay image phát hành.

## Cần nhớ

1. Firmware gọi bootloader; BIOS và UEFI tìm bootloader theo hai cơ chế khác nhau.
2. GRUB nạp kernel/initramfs và truyền command line.
3. initramfs giúp kernel tiếp cận root filesystem thật.
4. Kernel chạy init đầu tiên; init/system manager khởi chạy services.
5. SysVinit, systemd và Upstart là các họ init; distro hiện đại thường dùng systemd.
6. dmesg là kernel ring buffer; journalctl truy vấn journal, lịch sử tùy cấu hình.
7. Boot nhanh hơn chưa chắc tốt hơn; phải xác minh chức năng và khả năng khôi phục.

## Nguồn học tập

- [LPIC-1 Objectives V5.0 — Objective 101.2: Boot the system](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [LPI Learning Materials — LPIC-1 (101), Version 5.0, Lesson 101.2](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf)
- [LPI — LPIC-1: Systemd Beyond Services](https://www.lpi.org/blog/2019/01/29/lpic-1-systemd-beyond-services/)

