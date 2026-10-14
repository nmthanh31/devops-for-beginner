# Bài 5 — Service lifecycle: start, enable, reload, restart

> **Nền tảng LPIC-1 101.3:** chuyển runlevel/boot target, đặt target mặc định, shutdown/reboot, cảnh báo người dùng và kết thúc process đúng cách. Restart policy và `daemon-reload` là phần mở rộng vận hành.
>
> Nguồn: [LPI LPIC-1 Objectives V5.0](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0), mục 101.3; giáo trình: [LPIC-1 Learning Material (101), Version 5.0](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf).

## Mục tiêu

Chọn đúng thao tác systemd và hiểu thao tác nào ảnh hưởng manager, process hiện tại hoặc hành vi sau reboot.

## Các thao tác

| Lệnh | Tác động |
|---|---|
| systemctl start app | Yêu cầu start unit hiện tại |
| systemctl stop app | Yêu cầu dừng unit |
| systemctl restart app | Dừng rồi start lại |
| systemctl reload app | Yêu cầu application nạp lại runtime config nếu hỗ trợ |
| systemctl enable app | Thiết lập quan hệ kích hoạt ở boot/target sau |
| systemctl disable app | Gỡ quan hệ enable; không tự stop service đang chạy |
| systemctl daemon-reload | Manager đọc lại unit files và dependency |

## start khác enable

start tác động đến trạng thái hiện tại. enable thiết lập quan hệ để unit được target thích hợp kéo vào ở lần boot/activation sau. Enable không mặc định start ngay.

## reload khác daemon-reload

reload gửi yêu cầu tới service đang chạy để application nạp lại cấu hình. Chỉ dùng được nếu service hỗ trợ.

daemon-reload yêu cầu systemd manager đọc lại unit configuration. Nó không thay process hiện tại và không tự áp dụng ExecStart mới.

Khi sửa cấu hình unit làm thay cách chạy process, thường cần:

~~~text
daemon-reload → restart unit → verify process mới
~~~

Đánh giá impact trước khi restart service production.

## Restart policy

~~~ini
Restart=on-failure
RestartSec=3s
~~~

on-failure yêu cầu restart sau một số dạng failure mà systemd nhận diện; không có nghĩa restart sau mọi lần kết thúc. Start rate limiting như StartLimitIntervalSec và StartLimitBurst giúp ngăn restart loop.

Restart policy không sửa được cấu hình sai. Nó có thể chỉ làm lỗi lặp lại.

## Stop và graceful shutdown

Khi dừng service, systemd gửi signal theo unit config (thường mặc định là SIGTERM), chờ trong giới hạn thời gian rồi có thể dùng signal mạnh hơn nếu process không dừng.

~~~text
stop request → graceful signal → chờ → timeout policy nếu cần
~~~

TimeoutStopSec ảnh hưởng khoảng thời gian chờ. Application cần xử lý signal để hoàn tất request và cleanup.

## LPIC 101.3: target, shutdown và cảnh báo người dùng

Target là trạng thái vận hành mà systemd cần đưa máy tới. Dùng `systemctl get-default` để xem target mặc định; `systemctl set-default <target>` để đổi target mặc định cho lần boot sau; `systemctl isolate <target>` để chuyển target ngay. Rescue/single-user dùng cho bảo trì, còn emergency là môi trường tối thiểu hơn.

LPIC 101.3 cũng yêu cầu biết shutdown/reboot từ dòng lệnh, cảnh báo người dùng trước thay đổi lớn, và kết thúc process có trật tự. `shutdown` cho tiến trình thời gian dừng sạch, `wall` gửi thông báo tới phiên đăng nhập. Không thay shutdown đúng cách bằng cách ngắt điện hoặc kill hàng loạt process.

Lệnh xem trạng thái an toàn:

~~~bash
systemctl get-default
systemctl list-units --type=target
systemctl list-units --type=service --state=running
~~~

Các lệnh sau **chỉ thực hành trong VM dùng riêng**, vì chúng đổi trạng thái hoặc tắt máy:

~~~bash
sudo systemctl set-default multi-user.target
sudo systemctl isolate rescue.target
sudo shutdown -r +5 "Bao tri: may se khoi dong lai sau 5 phut"
sudo shutdown -c
~~~

`set-default` tác động đến lần boot sau; `isolate` tác động ngay; `shutdown` lên lịch reboot và gửi cảnh báo. `shutdown -c` hủy lịch vừa tạo nếu chưa tới giờ.

## Bài tập LPIC 101.3 — Lập kế hoạch đổi target (không thực thi)

Không chạy lệnh thay đổi trên máy đang dùng. Hãy viết ra: target mặc định hiện tại; lệnh nào xem target; khác nhau giữa đổi target mặc định và chuyển target ngay; cách thông báo người dùng trước khi reboot; vì sao cần để systemd kết thúc service/process đúng cách. Có thể xem trợ giúp bằng `shutdown --help` và `wall --help`.

## Lab 1 — So sánh enabled và active (read-only)

~~~bash
systemctl is-enabled cron.service
systemctl is-active cron.service
~~~

Nếu unit không tồn tại, thay bằng service hiện hữu. Ghi riêng:

- Có cấu hình tự kích hoạt không?
- Hiện tại có active không?

Giải thích vì sao hai câu trả lời không suy ra được từ nhau.

## Lab 2 — Lifecycle trên user service tạm

Sau khi tạo user unit riêng, ví dụ l02-lab-web.service:

~~~bash
systemctl --user start l02-lab-web.service
systemctl --user is-active l02-lab-web.service
systemctl --user restart l02-lab-web.service
systemctl --user stop l02-lab-web.service
systemctl --user enable --now l02-lab-web.service
systemctl --user is-enabled l02-lab-web.service
systemctl --user disable --now l02-lab-web.service
~~~

Chỉ thao tác trên unit user của lab. Không enable/disable service hệ thống để làm bài này. Ghi thao tác nào thay process hiện tại, thao tác nào thay hành vi kích hoạt sau này.

## Cần nhớ

start/stop/restart quản lý trạng thái chạy; enable/disable quản lý quan hệ kích hoạt; reload nói với application; daemon-reload nói với manager.
