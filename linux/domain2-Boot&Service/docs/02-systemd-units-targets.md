# Bài 2 — systemd, PID 1, unit và target

> **Nền tảng LPIC-1:** 101.2 (systemd trong boot) và 101.3 (boot target, đặt target mặc định, chuyển target). Các loại unit, thư mục unit và dependency graph được bổ sung để hiểu sâu hơn cách systemd vận hành.
>
> Nguồn: [LPI LPIC-1 Objectives V5.0](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0), mục 101.2–101.3; phần bổ sung: [LPI — systemd: Beyond Services](https://www.lpi.org/blog/2019/01/29/lpic-1-systemd-beyond-services/).

## Mục tiêu

Phân biệt systemd manager, unit, service và target; hiểu hệ thống đạt trạng thái mong muốn bằng dependency graph và jobs.

## systemd làm gì?

systemd system manager thường chạy với PID 1 trong userspace chính. Nó đọc unit configuration, tạo jobs, theo dõi trạng thái và quản lý vòng đời service.

systemd vẫn vận hành các Linux process thông thường, đồng thời bổ sung desired state, dependency và lifecycle management.

## Unit là gì?

Unit là đối tượng systemd quản lý. Nó có thể đại diện cho service, trạng thái nhóm, socket, mount, timer hoặc path.

| Unit type | Vai trò | Ví dụ |
|---|---|---|
| .service | Service hoặc tác vụ | sshd.service |
| .target | Nhóm/điểm đồng bộ unit | multi-user.target |
| .socket | Socket có thể kích hoạt service | name.socket |
| .mount | Mount point | home.mount |
| .timer | Kích hoạt theo lịch | backup.timer |
| .path | Kích hoạt khi path đổi | watch.path |

Một service không nhất thiết chỉ có một process; nó có thể quản lý nhiều process trong một cgroup.

## Target là gì?

Target là điểm hội tụ để nhóm hoặc đồng bộ unit. Target thường không phải application process và không sở hữu PID riêng cho ứng dụng.

- multi-user.target: môi trường nhiều người dùng, thường dùng trên server không GUI.
- graphical.target: môi trường đồ họa.
- rescue.target: môi trường phục hồi.
- emergency.target: môi trường cứu hộ tối thiểu.
- network.target: mốc liên quan network stack, không đảm bảo có kết nối.
- network-online.target: mốc online do cơ chế wait-online được cấu hình báo.

## Dependency graph và desired state

systemd không chỉ chạy một danh sách script tuần tự. Nó dựng jobs từ target và quan hệ unit; nhiều job có thể chạy song song khi dependency cho phép.

default.target xác định trạng thái mặc định cần đạt:

~~~text
default.target → dependency graph → jobs → services và unit khác
~~~

## Unit file và runtime state

- Unit file mô tả systemd nên quản lý unit như thế nào.
- Runtime state là trạng thái manager đang quan sát, ví dụ loaded, active, failed.

Sửa unit file không tự động thay process đang chạy. Cần phân biệt cấu hình trên disk, cấu hình manager đã nạp và process hiện tại.

Vị trí thường gặp:

| Vị trí | Vai trò |
|---|---|
| /usr/lib/systemd/system/ | Unit từ package/vendor |
| /lib/systemd/system/ | Vị trí trên một số distro |
| /etc/systemd/system/ | Unit và override do administrator quản lý |
| /run/systemd/system/ | Cấu hình runtime |

Với unit vendor, thường dùng drop-in override thay vì sửa trực tiếp file package.

## Lab 1 — Khám phá target (read-only)

~~~bash
systemctl get-default
systemctl list-units --type=target
systemctl list-dependencies multi-user.target
~~~

Ghi lại ba unit trong dependency output. Giải thích vì sao đây là quan hệ quản lý, không nhất thiết là PPID tree.

## Lab 2 — Đọc unit file hiện có (read-only)

~~~bash
systemctl list-unit-files --type=service
systemctl cat ssh.service
~~~

Nếu ssh.service không có, chọn một unit từ danh sách. Tìm các section [Unit], [Service], [Install]. Ghi vị trí file và giải thích unit đang khai báo điều gì.

## Cần nhớ

Unit là đối tượng systemd quản lý; service là một loại unit; target gom và đồng bộ unit. Dependency graph khác với process tree.
