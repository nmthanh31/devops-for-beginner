# Lab 2 — EnvironmentFile, kiểm tra trước khi chạy và restart policy

Đây là bài nâng cao hơn Lab 1. Bạn vẫn tự viết **user service**, nhưng lần này cấu hình nằm ở nhiều file và bạn sẽ cố tình làm process lỗi để quan sát systemd phục hồi.

## Mục tiêu

- dùng `EnvironmentFile` để tách cấu hình khỏi unit;
- hiểu `ExecStartPre` chạy kiểm tra trước `ExecStart`;
- chứng minh environment file đi vào process;
- phân biệt sửa unit với sửa environment file;
- quan sát `Restart=on-failure` sau lỗi process;
- xác nhận dừng service bằng `systemctl stop` không tạo vòng restart;
- đọc `systemctl status`, `show` và journal để tìm evidence.

## Quy tắc an toàn

Tất cả thao tác chỉ trên `l02-advanced.service` trong user manager. Khi thử gửi `SIGKILL`, hãy lấy và kiểm tra PID từ đúng unit trước; không dùng lệnh kill chung chung hoặc tác động vào PID khác.

## Bước 1 — Tạo webroot và file cấu hình

~~~bash
mkdir -p "$HOME/l02-advanced/webroot" "$HOME/.config/systemd/user"
printf 'Advanced service is running\n' > "$HOME/l02-advanced/webroot/index.html"
nano "$HOME/.config/systemd/user/l02-advanced.env"
~~~

Trong file `l02-advanced.env`, tự khai báo ba biến:

~~~text
APP_ENV=advanced-lab
HTTP_PORT=18082
BIND_ADDR=127.0.0.1
~~~

Đây là cú pháp file environment đơn giản: mỗi dòng là một cặp `KEY=VALUE`.

## Bước 2 — Tự viết unit nâng cao

Tạo file:

~~~bash
nano "$HOME/.config/systemd/user/l02-advanced.service"
~~~

Hãy viết các section và directive theo yêu cầu sau, không chép unit của Lab 1 rồi đoán:

### `[Unit]`

- Có `Description` mô tả đây là advanced training service.

### `[Service]`

- `Type=exec`.
- `WorkingDirectory` trỏ tới `$HOME/l02-advanced/webroot`. Trong file unit dùng đường dẫn tuyệt đối hoặc specifier `%h`; không ghi `$HOME` và mong systemd tự mở rộng.
- Nạp `$HOME/.config/systemd/user/l02-advanced.env` qua `EnvironmentFile`.
- Có `ExecStartPre` kiểm tra file `index.html` tồn tại trước khi chạy; dùng `/usr/bin/test -f ...`.
- `ExecStart` chạy Python HTTP server, dùng cổng và địa chỉ bind từ environment file. Gợi ý cú pháp command line systemd: `${HTTP_PORT}` và `${BIND_ADDR}`.
- Đặt `Restart=on-failure` và `RestartSec=2s`.
- Đặt `TimeoutStopSec=10s`.

### `[Install]`

- `WantedBy=default.target`.

Trước khi chạy, tự kiểm tra unit và environment file:

~~~bash
cat "$HOME/.config/systemd/user/l02-advanced.service"
cat "$HOME/.config/systemd/user/l02-advanced.env"
~~~

## Bước 3 — Nạp, chạy và kiểm tra HTTP

~~~bash
systemctl --user daemon-reload
systemctl --user start l02-advanced.service
systemctl --user status --no-pager l02-advanced.service
curl -i http://127.0.0.1:18082/
~~~

Nếu service không chạy, đừng restart lặp lại ngay. Đọc lỗi trước:

~~~bash
journalctl --user -u l02-advanced.service -n 30 --no-pager
systemctl --user cat l02-advanced.service
~~~

## Bước 4 — Xác minh cấu hình đã thành process

~~~bash
systemctl --user show l02-advanced.service -p MainPID -p ActiveState -p SubState -p NRestarts
~~~

Lấy `MainPID` từ output, rồi thay `<PID>` trong các lệnh sau:

~~~bash
ps -o pid,ppid,user,group,stat,cmd -p <PID>
readlink /proc/<PID>/cwd
tr '\0' '\n' < /proc/<PID>/environ | grep -E '^(APP_ENV|HTTP_PORT|BIND_ADDR)='
ss -lntp | grep ':18082'
~~~

Ghi nhận bằng chứng cho từng điều: process đang chạy; CWD đúng; environment được nạp; listener dùng đúng địa chỉ và port.

## Bước 5 — Thay đổi cấu hình environment

Sửa `HTTP_PORT` trong file `.env` từ `18082` thành `18083`. Sau đó chỉ restart service:

~~~bash
nano "$HOME/.config/systemd/user/l02-advanced.env"
systemctl --user restart l02-advanced.service
curl -i http://127.0.0.1:18083/
~~~

Ở đây không sửa unit file; systemd đọc environment file khi khởi chạy process, nên restart để process mới nhận giá trị. Ghi lại vì sao đổi nội dung `.env` không đồng nghĩa phải chạy `daemon-reload`.

## Bước 6 — Thử restart policy an toàn

Lấy PID ngay trước khi gửi signal:

~~~bash
systemctl --user show l02-advanced.service -p MainPID -p NRestarts
~~~

Kiểm tra chắc chắn service đang `active` và `MainPID` là PID của unit lab. Sau đó thay `<PID>` bằng đúng số PID vừa xem:

~~~bash
kill -KILL <PID>
~~~

Chờ vài giây rồi kiểm tra:

~~~bash
systemctl --user status --no-pager l02-advanced.service
systemctl --user show l02-advanced.service -p MainPID -p ActiveState -p NRestarts
journalctl --user -u l02-advanced.service -n 20 --no-pager
~~~

Trả lời: PID có đổi không? `NRestarts` có tăng không? Journal ghi nhận nguyên nhân restart thế nào? Vì sao `Restart=on-failure` áp dụng ở đây?

## Bước 7 — Dừng chủ động và so sánh

~~~bash
systemctl --user stop l02-advanced.service
systemctl --user is-active l02-advanced.service
systemctl --user show l02-advanced.service -p MainPID -p NRestarts
~~~

Service có tự sống lại sau lệnh `stop` không? Giải thích khác nhau giữa process chết do failure với việc administrator yêu cầu dừng unit.

## Bước 8 — Sửa unit và áp dụng đúng cách

Sửa `RestartSec=2s` thành `RestartSec=4s` trong unit file. Sau đó thực hiện theo thứ tự:

~~~text
daemon-reload → restart unit → kiểm tra lại cấu hình và trạng thái
~~~

Giải thích vì sao thay đổi unit cần `daemon-reload`, còn thay đổi file environment trong Bước 5 thì chỉ cần khởi chạy lại process.

## Tiêu chí hoàn thành

- [x] Unit do bạn tự viết và có đủ ba section.
- [x] HTTP trả nội dung từ đúng webroot.
- [x] Chứng minh được `APP_ENV`, `HTTP_PORT`, `BIND_ADDR` nằm trong environment của process.
- [x] `ExecStartPre` và `WorkingDirectory` trỏ đúng đường dẫn.
- [x] Có evidence restart policy hoạt động sau process failure.
- [x] Phân biệt được `stop`, `restart`, `daemon-reload`.
- [x] Đã dừng unit lab và xóa đúng file do bài tạo.

## Dọn lab

~~~bash
systemctl --user disable --now l02-advanced.service 2>/dev/null || systemctl --user stop l02-advanced.service
rm -f "$HOME/.config/systemd/user/l02-advanced.service"
rm -f "$HOME/.config/systemd/user/l02-advanced.env"
rm -f "$HOME/l02-advanced/webroot/index.html"
systemctl --user daemon-reload
rmdir "$HOME/l02-advanced/webroot" "$HOME/l02-advanced" 2>/dev/null || true
~~~

Chỉ xóa các file/thư mục có tên `l02-advanced` do bài này tạo.

## Nguồn tham khảo

- [systemd.service(5)](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)
- [systemd.exec(5)](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html)
