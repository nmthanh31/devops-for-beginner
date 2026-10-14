# Bài 4 — Service unit và execution context

> **Nền tảng và mở rộng:** LPIC-1 101.3 đặt nền tảng quản lý service/boot target bằng systemd. Cấu trúc unit chi tiết, execution context, drop-in và user service là phần thực hành mở rộng, nối kiến thức process của L01 với systemd.
>
> Nguồn phạm vi: [LPI LPIC-1 Objectives V5.0](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0), mục 101.3. Tham khảo service unit: [LPI — systemd: Beyond Services](https://www.lpi.org/blog/2019/01/29/lpic-1-systemd-beyond-services/), [systemd.service(5)](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html).

## Mục tiêu

Đọc một .service unit như bản khai báo cách systemd khởi chạy và quản lý process.

## Unit mẫu

~~~ini
[Unit]
Description=Lab HTTP API
Wants=network-online.target
After=network-online.target

[Service]
Type=exec
User=appuser
Group=appuser
WorkingDirectory=/opt/lab-api
EnvironmentFile=/etc/lab-api/app.env
ExecStart=/usr/bin/python3 /opt/lab-api/app.py
Restart=on-failure
RestartSec=3s
TimeoutStopSec=15s

[Install]
WantedBy=multi-user.target
~~~

Đây là ví dụ; user và path phải tồn tại mới chạy được.

## [Unit]: mô tả và quan hệ

- Description: mô tả unit.
- After/Before: ordering.
- Wants/Requires: requirement.
- ConditionPathExists: điều kiện để bỏ qua activation nếu không thỏa.
- RequiresMountsFor: kéo vào/sắp xếp mount cần để truy cập path.

## [Service]: cách tạo và quản lý process

| Directive | Liên hệ với process |
|---|---|
| ExecStart | Executable và arguments |
| User | User identity |
| Group | Group identity |
| WorkingDirectory | CWD |
| Environment | Environment inline |
| EnvironmentFile | Environment lấy từ file |
| StandardOutput | Nơi nhận stdout |
| StandardError | Nơi nhận stderr |
| Restart | Chính sách khi process kết thúc |
| KillSignal | Signal dùng khi dừng |

Đây là các khái niệm L01 được systemd cấu hình và quản lý.

EnvironmentFile không phải secret manager. Hãy bảo vệ quyền đọc file và đừng coi environment là nơi lưu secret tuyệt đối an toàn.

## [Install]: quan hệ enable

~~~ini
[Install]
WantedBy=multi-user.target
~~~

WantedBy được systemctl enable dùng để thiết lập quan hệ cho target kéo service vào. Nó không tự start process khi file được đọc.

## Drop-in override

Unit vendor thường nằm ở /usr/lib/systemd/system hoặc /lib/systemd/system. Administrator thường đặt override trong /etc/systemd/system/<unit>.d/.

Override thay đổi một số directive mà không sửa file vendor.

## Lab 1 — Đọc process context từ unit mẫu

Điền:

~~~text
Executable:
Arguments:
User:
Group:
CWD:
Environment source:
Restart policy:
Stop timeout:
Target liên quan khi enable:
~~~

Với từng mục, nối về L01: PID, UID/GID, environment, CWD, FD hoặc signal.

## Lab 2 — Tạo user service tạm để xem unit thành process

Lab này tạo một service chỉ trong user manager, bind loopback ở port 18080. Nó không sửa service hệ thống.

### Tạo unit file

~~~bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/l02-lab-web.service
~~~

Nội dung:

~~~ini
[Unit]
Description=L02 Training HTTP Service

[Service]
Type=exec
WorkingDirectory=/tmp
Environment=APP_ENV=training
ExecStart=/usr/bin/python3 -m http.server 18080 --bind 127.0.0.1
Restart=on-failure

[Install]
WantedBy=default.target
~~~

Nạp unit và khởi động:

~~~bash
systemctl --user daemon-reload
systemctl --user start l02-lab-web.service
~~~

Kiểm tra:

~~~bash
systemctl --user status l02-lab-web.service
systemctl --user show l02-lab-web.service -p MainPID -p ActiveState -p SubState
ss -lntp | grep ':18080'
curl -I http://127.0.0.1:18080
~~~

Liên hệ cấu hình với process:

~~~bash
MAINPID=$(systemctl --user show l02-lab-web.service -p MainPID --value)
ps -o pid,ppid,user,group,stat,cmd -p "$MAINPID"
readlink /proc/"$MAINPID"/cwd
tr '\0' '\n' < /proc/"$MAINPID"/environ | grep '^APP_ENV='
~~~

Nếu user manager không chạy hoặc Python nằm ở đường dẫn khác, đừng chuyển sang sửa service hệ thống. Ghi nhận điều kiện môi trường và hoàn thành Lab 1 bằng cách đọc unit mẫu.

### Dọn lab sau khi hoàn thành các bài tiếp theo

~~~bash
systemctl --user disable --now l02-lab-web.service
rm ~/.config/systemd/user/l02-lab-web.service
systemctl --user daemon-reload
~~~

Chỉ xóa unit lab vừa tạo.

## Cần nhớ

[Unit] mô tả metadata và quan hệ; [Service] mô tả cách chạy process; [Install] mô tả quan hệ được thiết lập khi enable.
