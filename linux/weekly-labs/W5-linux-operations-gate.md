# W5 Lab chính — Linux operations gate

| | |
|---|---|
| **Thời lượng** | Build/baseline ~2h + gate 8 fault (S5 · 90′ + SX nếu cần) |
| **Cần trước** | [L01–L12](../README.md), đặc biệt lab [L04](../domain4-Identity&Permissions/lab/01-least-privilege-service.md), [L09](../domain9-ResourceTroubleshooting/lab/01-resource-baseline.md), [L10](../domain10-HostNetworking/lab/01-host-network-evidence.md), [L12](../domain12-BackupRecovery/lab/01-backup-restore-hash.md) |
| **Gate G-Linux** | 8 fault phủ ≥ 8/12 domain; đúng ≥ 7, sửa ≥ 6; không `777`, reboot hay restart mù |

## Bạn sẽ chứng minh điều gì?

Một service hỏng có thể do nhiều lớp: process, systemd, quyền, filesystem, tài nguyên, mạng hoặc cấu hình bảo mật. Bạn phải khoanh vùng bằng bằng chứng, sửa đúng nguyên nhân và chứng minh service phục hồi. Bài này nối L01–L12; đọc lại [L09–L12](../README.md) trước khi làm.

Làm trên VM lab có console VMware. Giữ một phiên SSH đang hoạt động khi thử SSH/firewall. Mọi file, mount, service và rule thử nghiệm phải có tên riêng của lab; không thay đổi route hoặc firewall quản trị của VM nếu chưa có đường khôi phục qua console.

## Chuẩn bị baseline

1. Chọn một service HTTP lab đã chạy được. Ghi unit (`systemctl cat`), PID/status (`systemctl status`), listener (`ss -ltnp`), response (`curl -i`), log (`journalctl -u`) và đường dẫn data/config.
2. Ghi `uptime`, `free -h`, `vmstat 1 3`, `df -h`, `df -i`, `ip route get <client-IP>`, `getent hosts <hostname>`; dùng chúng làm mốc so sánh sau mỗi fault.
3. Sao lưu cấu hình lab và ghi SHA-256. Viết trước lệnh rollback tương ứng với từng thay đổi.

`status` cho biết unit và exit code; `journalctl` cho lỗi theo thời gian; `ss` chứng minh process đã bind vào IP:port nào; `curl` chứng minh HTTP ở phía client. Một phép kiểm PASS không thay thế các phép kiểm còn lại.

## Tám fault cần xử lý

Tạo lỗi **từng cái một**, bắt đầu từ trạng thái baseline. Có thể nhờ bạn học tạo fault kín; nếu tự làm, ghi dự đoán trước khi xem kết quả. Mỗi fault cần nêu giả thuyết, lệnh kiểm, bằng chứng, sửa tối thiểu, positive test, negative test và rollback.

| # | Domain | Fault lab | Bằng chứng cần tìm |
| --- | --- | --- | --- |
| 1 | L02 service | `WorkingDirectory` trong unit trỏ vào thư mục không tồn tại | `status`, `journalctl`, `systemctl cat`, `test -d` |
| 2 | L04 permission | User chạy service không đọc được file cấu hình hoặc `index.html` | `systemctl show -p User`, `namei -l`, `sudo -u USER test -r` |
| 3 | L05 storage | Mountpoint lab không được mount, service đọc nhầm thư mục nằm bên dưới | `findmnt`, `lsblk -f`, `df -h`, nội dung file sentinel |
| 4 | L07 logs/time | Timer lab không kích hoạt hoặc log cần tìm bị xem sai khoảng thời gian | `systemctl list-timers`, `journalctl -u ... --since`, `timedatectl` |
| 5 | L09 resource | Process lab tiêu thụ CPU hoặc memory vượt baseline; phân biệt với I/O wait | `top`/`ps`, `vmstat`, `free`, journal OOM nếu có |
| 6 | L10 network | Service bind `127.0.0.1` trong khi client kết nối bằng VM IP | `ss -ltnp`, `ip addr`, `curl` tại loopback và VM IP |
| 7 | L11 SSH/security | Quyền `~/.ssh/authorized_keys` hoặc allowlist lab sai làm key login thất bại | `ssh -v`, `sshd -T`, auth journal, quyền đường dẫn |
| 8 | L12 recovery | File cấu hình/data lab bị sửa sai; phục hồi từ backup đã kiểm hash | `sha256sum`, `diff`, archive listing, restore rồi test service |

Với fault 3, chỉ dùng filesystem và mountpoint lab; không sửa `/etc/fstab` của root filesystem. Với fault 5, giới hạn tải để VM vẫn điều khiển được và dừng process lab ngay sau khi thu bằng chứng. Với fault 7, kiểm key login trên một phiên mới trước mọi thay đổi; không tắt password auth hoặc khóa tài khoản quản trị trong bài này.

## Mẫu chẩn đoán cho từng fault

```text
Hiện tượng từ phía client:
Baseline trước lỗi:
Giả thuyết 1 / giả thuyết 2:
Lệnh và output phân biệt hai giả thuyết:
Nguyên nhân gốc:
Thay đổi tối thiểu:
Positive test (luồng đúng):
Negative test (luồng không được phép/sai phải fail):
Rollback và trạng thái cuối:
```

Nếu `curl` không kết nối được, đi từ tên/IP → route → listener → process → log. Nếu HTTP trả lỗi, xác định response do proxy hay app trả, rồi mới xem file và quyền. Nếu thấy `OOM`, đối chiếu thời điểm và process cụ thể; không mặc định mọi lỗi chậm là thiếu memory.

## Bài nộp và tiêu chí qua cổng

Nộp bảng 8 fault phủ ít nhất 8 trong 12 domain Linux, timeline, lệnh/output có timestamp, bản cấu hình trước/sau, checksum backup/restore và runbook khôi phục. Gate theo roadmap: xác định đúng nguyên nhân ít nhất **7/8**, sửa và xác minh ít nhất **6/8**. Không dùng `chmod 777`, reboot hoặc restart hàng loạt để che nguyên nhân.

Sau bài, trả service, mount, rule và file lab về baseline; kiểm lại `systemctl status`, `findmnt`, `ss`, `curl` và SSH ở phiên mới.

Nguồn: [LPIC-1 objectives](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0), [LPIC-2 objectives V4.5](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5).
