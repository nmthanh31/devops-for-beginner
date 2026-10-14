# Lab 1 — Viết user service HTTP đầu tiên

## Mục tiêu

Tự viết một service unit và giải thích được từng dòng quan trọng:

- `[Unit]`, `[Service]`, `[Install]` mô tả những gì;
- `WorkingDirectory` ảnh hưởng nơi chương trình tìm file như thế nào;
- `ExecStart` khởi chạy chương trình nào;
- `Environment` truyền biến môi trường vào process;
- `index.html` là nội dung web được HTTP server phục vụ;
- vì sao bài lab dùng `systemctl --user`.

## Kết quả mong muốn

Một Python HTTP server chạy dưới user manager, bind vào `127.0.0.1:18081`, trả về nội dung `index.html` khi truy cập `/`.

## Bước 1 — Chuẩn bị nội dung website

~~~bash
mkdir -p "$HOME/l02-webroot" "$HOME/.config/systemd/user"
printf 'Hello from my systemd service\n' > "$HOME/l02-webroot/index.html"
cat "$HOME/l02-webroot/index.html"
~~~

`index.html` là file nội dung website. Python HTTP server tìm file trong `WorkingDirectory`. Khi client yêu cầu `/`, server trả `index.html` nếu file tồn tại; nếu không, server thường trả danh sách file trong thư mục.

## Bước 2 — Tự viết unit file

Mở file:

~~~bash
nano "$HOME/.config/systemd/user/l02-practice.service"
~~~

Tự tạo đủ ba section `[Unit]`, `[Service]`, `[Install]` theo yêu cầu:

| Thuộc tính | Giá trị cần dùng |
|---|---|
| Description | Mô tả ngắn cho service |
| Type | `exec` |
| WorkingDirectory | Đường dẫn tuyệt đối tới thư mục `l02-webroot` của bạn |
| Environment | `APP_ENV=training` |
| ExecStart | `/usr/bin/python3 -m http.server 18081 --bind 127.0.0.1` |
| Restart | `on-failure` |
| WantedBy | `default.target` |

Trong unit file không viết `~` hoặc `$HOME` cho `WorkingDirectory`; systemd không chạy dòng đó qua shell để mở rộng các ký hiệu này. Hãy tìm đường dẫn home bằng `echo "$HOME"`, rồi ghi đường dẫn đầy đủ.

Trước khi chạy, tự kiểm tra file:

~~~bash
cat "$HOME/.config/systemd/user/l02-practice.service"
~~~

## Bước 3 — Nạp và khởi động service

~~~bash
systemctl --user daemon-reload
systemctl --user start l02-practice.service
systemctl --user status --no-pager l02-practice.service
~~~

`daemon-reload` bảo manager đọc lại unit file. `start` yêu cầu chạy service ngay bây giờ; nó không tự bật service mỗi lần đăng nhập.

## Bước 4 — Kiểm tra nội dung được phục vụ

~~~bash
curl -i http://127.0.0.1:18081/
ss -lntp | grep ':18081'
~~~

Kết quả `curl` cần có HTTP response và dòng `Hello from my systemd service`. Server chỉ bind `127.0.0.1`, nên không thể truy cập trực tiếp từ máy khác.

## Bước 5 — Nối unit với process

~~~bash
systemctl --user show l02-practice.service -p MainPID -p ActiveState -p SubState
~~~

Ghi lại `MainPID`, rồi dùng PID đó thay vào `<PID>`:

~~~bash
ps -o pid,ppid,user,group,stat,cmd -p <PID>
readlink /proc/<PID>/cwd
tr '\0' '\n' < /proc/<PID>/environ | grep '^APP_ENV='
~~~

Kỳ vọng thấy process Python, CWD là thư mục `l02-webroot`, và `APP_ENV=training`. Đây là cách nối cấu hình unit với process thật.

## Câu hỏi tự kiểm tra

1. `index.html` được systemd đọc hay được Python HTTP server đọc?
2. Nếu đổi `WorkingDirectory` sang thư mục không có `index.html`, `curl /` sẽ cho kết quả gì?
3. `start` khác `enable` ở điểm nào?
4. Vì sao unit này cần `systemctl --user`?
5. `APP_ENV` được khai báo trong unit thì process nhận biến đó bằng cách nào?

## Dọn lab

~~~bash
systemctl --user disable --now l02-practice.service 2>/dev/null || systemctl --user stop l02-practice.service
rm -f "$HOME/.config/systemd/user/l02-practice.service" "$HOME/l02-webroot/index.html"
systemctl --user daemon-reload
rmdir "$HOME/l02-webroot" 2>/dev/null || true
~~~

Lệnh dọn chỉ xóa unit và file nội dung do bài này tạo.

## Đáp án tham khảo

Chỉ xem sau khi đã tự viết:

~~~ini
[Unit]
Description=Lab 02 Service

[Service]
Type=exec
WorkingDirectory=/home/setup/l02-webroot
Environment=APP_ENV=training
ExecStart=/usr/bin/python3 -m http.server 18081 --bind 127.0.0.1
Restart=on-failure

[Install]
WantedBy=default.target
~~~

Thay `/home/setup` bằng home directory thực tế của bạn nếu khác.
