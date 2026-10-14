# Bài 8 — Troubleshooting service và boot timing

> **Nền tảng và mở rộng:** LPIC-1 101.2 yêu cầu xem boot events trong log; 101.3 yêu cầu quản lý target/service. Quy trình điều tra áp dụng các mục tiêu đó; `systemd-analyze`, HTTP health và property chi tiết là phần mở rộng thực hành, không phải danh sách kiến thức thi LPIC.
>
> Nguồn phạm vi: [LPI LPIC-1 Objectives V5.0](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0), mục 101.2–101.3. Tham khảo phần timing mở rộng: [systemd-analyze(1)](https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html).

## Mục tiêu

Điều tra service từ evidence thay vì restart theo phản xạ; phân biệt lỗi unit, process, socket, HTTP và boot delay.

## Triệu chứng thường gặp

| Triệu chứng | Nguyên nhân có thể | Evidence ưu tiên |
|---|---|---|
| Service không start | Executable, user, CWD, config, mount, dependency | status, journalctl, show, cat |
| Active nhưng không listen | App chưa bind, sai port, process con lỗi | ss, ps, /proc, journal |
| Restart liên tục | Crash, exit code, timeout, rate limit | journal, Result, ExecMainStatus, NRestarts |
| Không chạy sau reboot | Chưa enable, target/dependency, boot-time mount/config | is-enabled, dependencies, boot journal |

## Trình tự thu evidence

### 1. Trạng thái tổng quan

~~~bash
systemctl status example.service
~~~

Đọc Loaded, Active, Main PID, Result và log gần nhất.

### 2. Runtime properties

~~~bash
systemctl show example.service \
  -p LoadState \
  -p ActiveState \
  -p SubState \
  -p Result \
  -p ExecMainStatus \
  -p MainPID \
  -p NRestarts
~~~

### 3. Log đúng unit và boot

~~~bash
journalctl -b -u example.service --no-pager
~~~

### 4. Cấu hình manager thấy

~~~bash
systemctl cat example.service
~~~

### 5. Dependency

~~~bash
systemctl list-dependencies example.service
~~~

### 6. Process rồi đến socket/HTTP

~~~bash
ps -fp <MainPID>
ss -lntp
curl -i http://127.0.0.1:<port>/healthz
~~~

Đi đến kết luận sau khi tách được cấu hình, process, socket và application.

## Vì sao không restart ngay?

Restart có thể làm mất trạng thái process ban đầu, thay đổi timing, che lỗi tái hiện và không sửa root cause. Trước tiên ghi baseline, lập giả thuyết, thay đổi tối thiểu rồi verify. Với production cần xét impact và quy trình change.

## Boot timing

~~~bash
systemd-analyze time
systemd-analyze blame
systemd-analyze critical-chain
~~~

- time: tổng quan các mốc firmware/kernel/initrd/userspace khi hệ thống cung cấp.
- blame: activation duration của unit có thể đo phù hợp.
- critical-chain: chuỗi timing dependency ảnh hưởng mốc target/unit được phân tích.

Không kết luận unit đầu bảng blame tự động là nguyên nhân boot chậm. Nhiều unit chạy song song; activation duration không đồng nghĩa toàn bộ thời gian nằm trên critical path.

Kiểm tra unit file:

~~~bash
systemd-analyze verify /etc/systemd/system/example.service
~~~

verify phát hiện một số lỗi cấu hình nhưng không chứng minh service runtime hoặc application healthy.

## Lab 1 — Tình huống active nhưng HTTP lỗi

Tình huống: service báo active (running), nhưng người dùng không gọi được HTTP endpoint.

Không chạy lệnh. Viết thứ tự kiểm tra theo chuỗi:

~~~text
unit state → MainPID → process context → socket/bind address → HTTP → dependency/log
~~~

Trả lời:

1. Nếu không có listener, có thể lỗi ở tầng nào?
2. Nếu listener có nhưng HTTP 503, điều đó chứng minh và chưa chứng minh gì?
3. Nếu HTTP local đúng nhưng remote không vào được, cần kiểm tra tầng nào?

## Lab 2 — Đọc boot timing (read-only)

~~~bash
systemd-analyze time
systemd-analyze blame
systemd-analyze critical-chain
~~~

Chọn unit có duration cao trong blame và tìm nó trong critical-chain. Ghi:

- Có nằm trên chuỗi quan trọng không?
- Mốc nào bị ảnh hưởng?
- Vì sao vẫn cần xem dependency và target thực tế?

## Cần nhớ

Đi từ unit đến process, socket rồi application response. active, LISTEN và HTTP healthy là các bằng chứng khác nhau. Timing tools giúp định hướng, không tự xác định root cause.
