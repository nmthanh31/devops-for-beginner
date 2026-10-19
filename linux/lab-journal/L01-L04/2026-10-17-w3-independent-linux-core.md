# 2026-10-17 — Tự dựng độc lập Linux core (L01–L04)

## Mục tiêu

Tự dựng một HTTP service tĩnh từ đầu, rồi dùng bằng chứng để giải thích quan hệ giữa user/group, quyền trên filesystem, systemd unit, process và listener.

## Phạm vi an toàn

- Làm trên VM lab an toàn; không reboot hoặc sửa service của cluster/máy dùng chung.
- Dùng một tên unit, user, thư mục và port dành riêng cho bài lab.
- Nếu chỉ có thể dùng `systemctl --user`, ghi rõ bài chưa chứng minh system service chạy dưới user riêng `l04app`.
- Không dùng `chmod 777`; không đưa secret vào file ghi chép.

## Đề bài

Tạo service `l04-lab-api.service` đáp ứng các điều kiện:

- Chạy bằng user riêng `l04app`, không chạy bằng `root`.
- Phục vụ file `index.html` có nội dung tự viết.
- Phần lab cốt lõi bind vào `127.0.0.1` trên một port còn trống.
- Có working directory, cấu hình môi trường và data path riêng cho lab.
- Được systemd quản lý và trả đúng nội dung qua HTTP.
- Quyền trên file và từng thư mục cha đủ cho service đọc dữ liệu, nhưng không rộng hơn cần thiết.

Phần mở rộng: đổi bind sang IP của VM để Windows host truy cập được; đây là thay đổi exposure của service, cần làm riêng sau khi chứng minh phần loopback.

## Kế hoạch trước khi chạy

### 20 phút đầu — không xem notes

- [ ] Vẽ luồng `systemd → process → UID/GID → file/path → socket → HTTP response`.
- [ ] Phác thảo các đường dẫn sẽ dùng và ai sở hữu từng đường dẫn.
- [ ] Viết test matrix: service active, PID/identity đúng, listener đúng địa chỉ, HTTP đúng nội dung, negative test.
- [ ] Dự đoán quyền cần có trên thư mục và file.

### Thực hiện độc lập

- [ ] Tạo user/group `l04app` và cấu trúc thư mục riêng.
- [ ] Tạo trang `index.html` và cấu hình môi trường không chứa secret.
- [ ] Viết unit systemd với user/group, working directory, environment/configuration, command và restart policy phù hợp.
- [ ] Khởi động service; kiểm tra status và log.
- [ ] Xác minh process identity, PID/PPID, cwd và environment.
- [ ] Xác minh listener chỉ bind `127.0.0.1` và HTTP trả đúng trang.
- [ ] Dùng `stat`/`namei` giải thích owner, mode và quyền traverse trên đường dẫn.
- [ ] Chạy negative test: xác nhận không truy cập được qua địa chỉ không được phép, hoặc chứng minh service không có quyền ghi nếu chỉ cần đọc.
- [ ] Ghi lại lệnh, dự đoán, output quan trọng và diễn giải.

## Hướng dẫn thực hiện — lệnh và ý nghĩa

### 1. Kiểm tra user, unit, thư mục và port trước khi tạo

~~~bash
getent passwd l04app || true
systemctl cat l04-lab-api.service 2>/dev/null || true
ls -ld /var/lib/l04-lab-api 2>/dev/null || true
ss -ltn 'sport = :18082'
~~~

- `getent passwd l04app`: tra cứu tài khoản `l04app` qua cơ chế user database của Linux. Nếu đã có, không tạo hoặc sửa tài khoản đó một cách mù quáng.
- `|| true`: cho phép tiếp tục khi mục kiểm tra không tìm thấy đối tượng; nó không sửa lỗi của lệnh trước.
- `systemctl cat ...`: in nội dung unit nếu đã có. `2>/dev/null` ẩn thông báo lỗi khi unit chưa tồn tại.
- `ls -ld PATH`: xem metadata của chính path (`-d`), ở dạng chi tiết (`-l`), không liệt kê nội dung thư mục.
- `ss -ltn 'sport = :18082'`: xem TCP listener (`-l -t`), hiển thị port số (`-n`), lọc chính xác port 18082. Nếu ngoài header có dòng socket, hãy chọn port khác.

Nếu user, unit hoặc data path đã tồn tại thì chọn tên lab khác thay vì ghi đè. Nếu port đã có listener thì chọn port trống và thay đồng bộ trong unit/curl.

### 2. Tạo service account

Chỉ chạy khi bước kiểm tra xác nhận user chưa tồn tại:

~~~bash
sudo useradd --system --user-group --no-create-home --shell /usr/sbin/nologin l04app
id l04app
getent passwd l04app
~~~

- `sudo`: chạy thao tác cần quyền quản trị.
- `useradd`: tạo tài khoản.
- `--system`: tạo tài khoản hệ thống, không dành cho đăng nhập thường.
- `--user-group`: tạo group chính cùng tên `l04app`.
- `--no-create-home`: không tạo home directory.
- `--shell /usr/sbin/nologin`: không cho tài khoản mở shell đăng nhập.
- `id` xác nhận UID/GID và groups; `getent passwd` xác nhận thông tin tài khoản qua hệ thống lookup.

### 3. Tạo data path với quyền đọc vừa đủ

~~~bash
sudo install -d -o root -g l04app -m 0750 \
  /var/lib/l04-lab-api \
  /var/lib/l04-lab-api/www
~~~

`install -d` tạo thư mục. `-o root` đặt owner là root; `-g l04app` đặt group; `-m 0750` đặt quyền owner `rwx`, group `r-x`, other không có quyền. Dấu `\` ở cuối dòng nối lệnh sang dòng kế tiếp trong shell.

Tạo trang mẫu:

~~~bash
sudo tee /var/lib/l04-lab-api/www/index.html >/dev/null <<'EOF'
<!doctype html>
<html>
  <head><title>Linux Lab</title></head>
  <body>
    <h1>L04 Lab API</h1>
    <p>Service is running as a dedicated user.</p>
  </body>
</html>
EOF

sudo chown root:l04app /var/lib/l04-lab-api/www/index.html
sudo chmod 0640 /var/lib/l04-lab-api/www/index.html
~~~

- `tee PATH` nhận nội dung từ stdin và ghi vào file. `sudo` cho phép ghi vào thư mục hệ thống; `>/dev/null` bỏ phần nội dung `tee` echo ra terminal.
- `<<'EOF' ... EOF` là here-document. Dấu nháy giữ nội dung nguyên văn, không để shell khai triển biến.
- `chown root:l04app`: owner `root`, group `l04app`.
- `chmod 0640`: owner đọc/ghi, group chỉ đọc, other không có quyền. Vì thế service đọc được file qua group nhưng không sửa được.

Kiểm tra đường dẫn và metadata:

~~~bash
namei -l /var/lib/l04-lab-api/www/index.html
stat -c '%A %U:%G %n' /var/lib/l04-lab-api /var/lib/l04-lab-api/www /var/lib/l04-lab-api/www/index.html
~~~

`namei -l` hiển thị quyền trên từng thành phần của đường dẫn. `stat -c` chọn format: `%A` mode, `%U` owner, `%G` group, `%n` tên path. Muốn mở file, process cần traverse (`x`) qua từng thư mục cha và có quyền đọc (`r`) trên file.

### 4. Viết unit systemd

~~~bash
sudoedit /etc/systemd/system/l04-lab-api.service
~~~

`sudoedit` mở file bằng editor với quyền phù hợp, tránh chạy editor đồ họa/toàn bộ editor dưới root. Nội dung unit:

~~~ini
[Unit]
Description=L04 Linux Lab Service
After=network.target

[Service]
Type=exec
User=l04app
Group=l04app
WorkingDirectory=/var/lib/l04-lab-api/www
Environment=APP_ENV=training
ExecStart=/usr/bin/python3 -m http.server 18082 --bind 127.0.0.1
Restart=on-failure

[Install]
WantedBy=multi-user.target
~~~

- `[Unit]`, `[Service]`, `[Install]` chia cấu hình theo nhóm.
- `Description` là tên đọc được; `After=network.target` đặt thứ tự khởi động, không đảm bảo mọi mạng đã sẵn sàng.
- `Type=exec`: systemd coi service đã bắt đầu khi lệnh được thực thi thành công.
- `User`/`Group`: identity process sẽ chạy.
- `WorkingDirectory`: cwd của process.
- `Environment`: thêm biến vào environment. `APP_ENV` phục vụ quan sát; Python HTTP server mẫu không sử dụng biến này.
- `ExecStart`: executable `/usr/bin/python3`; `-m http.server` chạy module HTTP server; `18082` là port; `--bind 127.0.0.1` giới hạn listener trong VM.
- `Restart=on-failure`: tự khởi động lại khi process thoát do lỗi.
- `WantedBy=multi-user.target`: target dùng khi enable unit; riêng `start` không tự enable unit.

Lưu/thoát tùy editor: trong Vim nhấn `Esc`, gõ `:wq`, Enter; trong Nano nhấn `Ctrl+O`, Enter, rồi `Ctrl+X`. Các phím/lệnh đó phải nhập khi đang ở editor, không nhập tại dấu nhắc shell. Xem nội dung đã lưu bằng `systemctl cat l04-lab-api.service`.

### 5. Nạp cấu hình, chạy và đọc log

~~~bash
sudo systemctl daemon-reload
sudo systemctl start l04-lab-api.service
systemctl status l04-lab-api.service --no-pager
sudo journalctl -u l04-lab-api.service -n 20 --no-pager
~~~

- `daemon-reload`: systemd manager đọc lại file unit; lệnh này **không tự restart process đang chạy**.
- `start`: khởi chạy service.
- `status`: xem trạng thái; `--no-pager` in thẳng ra terminal.
- `journalctl -u UNIT -n 20`: lọc log theo unit (`-u`) và lấy 20 dòng (`-n`).

Sau khi chỉnh unit đang chạy, dùng `sudo systemctl restart l04-lab-api.service` để process mới nhận cấu hình. Nếu start/restart lỗi, đọc status và journal trước khi đổi cấu hình.

### 6. Chứng minh process context

~~~bash
pid=$(systemctl show -p MainPID --value l04-lab-api.service)
echo "PID=$pid"
ps -o pid,ppid,user,group,args -p "$pid"
readlink "/proc/$pid/cwd"
sudo cat "/proc/$pid/environ" | tr '\0' '\n' | grep '^APP_ENV='
sudo ls -l "/proc/$pid/fd"
~~~

- `systemctl show -p MainPID --value`: lấy PID chính; `-p` chọn property, `--value` bỏ tên property.
- `pid=$(...)`: lưu kết quả vào biến shell.
- `ps -o ... -p PID`: chọn cột PID/PPID/user/group/args và chỉ xem PID đó.
- `/proc/PID/cwd` là liên kết tới cwd; `readlink` in đích.
- `environ` chứa các biến ngăn bởi NUL; `tr '\0' '\n'` đổi NUL thành newline; `grep` lọc `APP_ENV`.
- `fd` chứa các file descriptor đang mở; `ls -l` cho thấy chúng trỏ tới đâu.

Chỉ kiểm tra environment của lab này vì nó không chứa secret; environment của service thật có thể chứa dữ liệu nhạy cảm.

### 7. Xác minh quyền, listener và HTTP trong VM

~~~bash
sudo -u l04app test -r /var/lib/l04-lab-api/www/index.html && echo 'l04app can read'

if sudo -u l04app test -w /var/lib/l04-lab-api/www/index.html; then
  echo 'l04app can write'
else
  echo 'Good: l04app cannot write'
fi

ss -ltnp | grep ':18082'
curl -i http://127.0.0.1:18082/
~~~

- `sudo -u l04app COMMAND`: chạy phép thử dưới identity của service.
- `test -r FILE` kiểm tra quyền đọc; `test -w FILE` kiểm tra quyền ghi.
- `if` chọn thông báo theo kết quả; expected là đọc được, không ghi được.
- `ss -ltnp`: listener TCP, port dạng số, kèm process nếu có quyền xem; `grep` lọc dòng port.
- `curl -i URL`: gửi HTTP request và in cả header lẫn body.

### 8. Mở rộng: truy cập từ Windows host

Phần này đổi phạm vi truy cập từ loopback sang interface VM. Trước hết xác nhận IP thật của VM:

~~~bash
ip -br addr
~~~

`ip` xem network state; `-br` in dạng ngắn gọn. Chỉ dùng IP được gán cho VM. Trong lab này là `192.168.220.133`.

Mở unit bằng `sudoedit` và đổi riêng `ExecStart` thành:

~~~ini
ExecStart=/usr/bin/python3 -m http.server 18082 --bind 192.168.220.133
~~~

Bind vào IP cụ thể thay vì `127.0.0.1` để nhận kết nối tới interface VM. Không dùng `0.0.0.0` nếu không chủ ý nghe trên tất cả interface.

Nạp cấu hình, restart và kiểm tra từ trong VM:

~~~bash
sudo systemctl daemon-reload
sudo systemctl restart l04-lab-api.service
systemctl status l04-lab-api.service --no-pager
ss -ltnp | grep ':18082'
curl http://192.168.220.133:18082/
~~~

`daemon-reload` đọc lại unit; `restart` thay process cũ bằng process nhận bind mới. `ss` cần hiện `192.168.220.133:18082`; `curl` xác minh HTTP qua IP đó ngay trong VM.

Sau đó, mở **Windows PowerShell trên máy Windows** (không chạy trong SSH/Linux terminal):

~~~powershell
Test-NetConnection 192.168.220.133 -Port 18082
~~~

`Test-NetConnection` là cmdlet PowerShell; `-Port` chọn TCP port cần thử. Nếu `TcpTestSucceeded` là `True`, mở `http://192.168.220.133:18082/` trên trình duyệt Windows. Nếu thất bại, kiểm tra VM network mode và firewall; không tắt firewall hay mở mọi interface một cách mù quáng.

Không gõ nguyên chữ `VM_IP` trong URL: đó chỉ là placeholder cần thay bằng IP thật. Lỗi `Could not resolve host: VM_IP` nghĩa là curl đã coi chuỗi đó như hostname. Lỗi kết nối tới IP thật khi listener vẫn chỉ bind `127.0.0.1` là điều dự kiến. `Test-NetConnection: command not found` nghĩa là cmdlet PowerShell bị chạy trong Linux shell.

## Dừng service sau lab

~~~bash
sudo systemctl stop l04-lab-api.service
~~~

`stop` dừng process nhưng giữ lại unit, user và data để xem lại bằng chứng. Không cần reboot hoặc enable để hoàn thành bài. Nếu xóa lab, xác nhận từng target đúng là artifact riêng của bài; không xóa user `l04app` trước khi chắc chắn service khác không dùng nó.

## Bảng kết quả

| Kiểm tra | Dự đoán | Kết quả thực tế | Bằng chứng / diễn giải |
|---|---|---|---|
| Service state | | | |
| User/group của process | `l04app:l04app` | | |
| PID/PPID/cwd/environment | | | |
| Listener address/port | Cốt lõi: `127.0.0.1:18082`; mở rộng Windows: `192.168.220.133:18082` | | |
| HTTP response | | | |
| Owner/mode và path traversal | | | |
| Negative test | | | |

## Definition of Done

- [ ] Service chạy thành công dưới `l04app`, không phải root.
- [ ] HTTP trả đúng nội dung trên `127.0.0.1`.
- [ ] Process, unit, filesystem path và listener được nối bằng evidence.
- [ ] Giải thích được vì sao thiếu quyền `x` ở một thư mục cha có thể chặn truy cập file.
- [ ] Không dùng `chmod 777`; quyền được đặt theo least privilege.
- [ ] README này đủ rõ để người khác tái lập bài lab.

## Troubleshooting log

| Triệu chứng | Bằng chứng trước khi sửa | Nguyên nhân | Sửa tối thiểu | Verify sau sửa |
|---|---|---|---|---|
| `curl http://VM_IP:18082/` báo không resolve host | Gõ literal `VM_IP` trong URL | Placeholder chưa được thay bằng IP thật | Dùng IP VM thực tế | Chạy curl tới IP thật |
| Curl tới IP VM không kết nối sau khi sửa unit | Unit mới có `--bind 192.168.220.133`, nhưng process cũ chưa restart | `daemon-reload` chỉ nạp cấu hình; không thay process đang chạy | `sudo systemctl restart l04-lab-api.service` | `ss` hiện bind IP mới; curl trong VM thành công |
| `Test-NetConnection` báo command not found | Lệnh chạy tại prompt Linux `setup@k8s-wk` | Đây là cmdlet PowerShell, không phải lệnh Linux | Chạy trên Windows PowerShell | `TcpTestSucceeded` hiển thị kết quả TCP |
| Gõ `wq` tại prompt shell báo command not found | Đã thoát khỏi `sudoedit` về shell | `wq` chỉ thao tác bên trong Vim; unit vẫn đã lưu nếu `systemctl cat` hiện nội dung mới | Dùng `Esc`, `:wq`, Enter khi còn ở Vim; xác nhận bằng `systemctl cat` | Nội dung unit hiển thị đúng |
| | | | | |

## Cleanup

Ghi lại những gì đã dừng/xóa và xác nhận không đụng đến service hoặc dữ liệu ngoài phạm vi lab. Chỉ dọn các đường dẫn và unit dành riêng cho bài này. Nếu chưa cần xóa, có thể giữ lại unit và data sau khi đã stop service để xem evidence.

## Explain-back

1. systemd tạo hoặc quản lý process nào trong bài lab?
2. Process chạy với UID/GID nào, và kiểm tra bằng chứng ở đâu?
3. Vì sao quyền trên từng thư mục cha ảnh hưởng việc đọc `index.html`?
4. `active (running)` chứng minh điều gì, và chưa chứng minh điều gì?

## Review

- Điều tự làm được mà không cần notes:
- Chỗ phải tra cứu:
- Một điều sẽ nhớ cho lần sau:
- D+1: vẽ lại flow trong 5 phút, không notes.
