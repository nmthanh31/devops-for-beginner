# Bài 6 — Service type, startup và readiness

> **Phần mở rộng vận hành:** LPIC-1 101.2/101.3 dạy quá trình boot và quản lý target/service ở mức nền tảng. Chi tiết `Type=`, listener và HTTP readiness ở đây giúp chẩn đoán thực tế, không phải phần cốt lõi cần thuộc cho LPIC.
>
> Nguồn phạm vi: [LPI LPIC-1 Objectives V5.0](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0). Tham khảo `Type=` và readiness notification: [systemd.service(5)](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html).

## Mục tiêu

Hiểu “systemd coi unit đã start” không đồng nghĩa “application sẵn sàng nhận traffic”.

## Vì sao có Type?

systemd cần một mốc xác định startup đã hoàn tất. Mốc đó phụ thuộc Type.

| Type | Mốc khởi động chính |
|---|---|
| simple | Manager đánh dấu startup rất sớm sau khi tạo process |
| exec | Chờ execve thành công; phát hiện một số lỗi thực thi |
| notify | Application thông báo readiness, thường là READY=1 |
| forking | Hỗ trợ daemon truyền thống tự fork rồi parent thoát |
| oneshot | Tác vụ hữu hạn; lệnh hoàn tất là một phần mốc startup |
| dbus | Dùng việc sở hữu D-Bus name làm mốc |

exec thường phù hợp với nhiều service foreground. Nó không chứng minh app mở port hay kết nối database.

notify cần application hoặc wrapper hỗ trợ systemd notification protocol. Chỉ đổi Type không khiến app bất kỳ tự gửi readiness.

## Ba trạng thái khác nhau

~~~text
systemd unit active
≠ kernel socket LISTEN
≠ application ready
~~~

Ví dụ:

| Thành phần | Trạng thái |
|---|---|
| Python process | Running |
| systemd unit | active (running) |
| TCP port | Listening |
| HTTP /healthz | 503 |
| Database | Unavailable |

## Liveness, readiness, dependency health

- Liveness: process/app còn khả năng hoạt động không?
- Readiness: app có thể nhận traffic mới chưa?
- Dependency health: database, storage hoặc downstream cần thiết có đáp ứng không?

systemd không tự áp dụng HTTP readiness probe phổ quát. Cần thiết kế endpoint hoặc kiểm chứng phù hợp.

## Chuỗi readiness cần kiểm chứng

~~~text
systemd state → MainPID/process → socket đúng IP:port
              → HTTP endpoint → response và dependency
~~~

Mỗi lớp loại trừ một số nguyên nhân nhưng chưa chứng minh lớp kế tiếp.

## Lab 1 — Đọc Type và state (read-only)

~~~bash
systemctl show cron.service -p Type -p ActiveState -p SubState -p MainPID
~~~

Nếu không có cron.service, dùng unit có sẵn. Ghi Type, MainPID, điều output chứng minh và điều chưa chứng minh về readiness.

## Lab 2 — Phân biệt active, listener và HTTP

Chọn HTTP service đang chạy:

~~~bash
systemctl is-active <service>
ss -lntp
curl -i http://127.0.0.1:<port>/healthz
~~~

Nếu không có endpoint health, thử / và ghi rõ đây chỉ chứng minh HTTP response, không phải readiness logic. Có thể dùng user HTTP service tạm sau khi hoàn thành Bài 4.

## Cần nhớ

Type quyết định mốc systemd đánh giá startup; readiness ứng dụng cần kiểm tra riêng bằng socket, HTTP và dependency phù hợp.
