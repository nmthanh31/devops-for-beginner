# L02 — Labs: systemd Service

Các bài lab này dùng **user service** để bạn luyện viết unit mà không sửa dịch vụ toàn hệ thống. Chạy lệnh quản lý service với `systemctl --user`.

## Lộ trình

1. [Lab 1 — Viết user service HTTP đầu tiên](./01-write-first-user-service.md): viết một unit cơ bản, chạy Python HTTP server và hiểu `index.html`, `WorkingDirectory`, `ExecStart`.
2. [Lab 2 — Service dùng EnvironmentFile và tự phục hồi](./02-environment-restart-user-service.md): tự viết unit nâng cao hơn, đọc biến môi trường, kiểm tra `ExecStartPre`, restart policy, journal và thay đổi cấu hình.

## Quy tắc an toàn

- Không dùng `sudo systemctl` cho các bài này; đó là system manager, phạm vi toàn máy.
- Chỉ quản lý hai unit lab bằng `systemctl --user`.
- Chưa `enable` service cho đến khi hiểu rõ hành vi sau đăng nhập/reboot.
- Khi thử restart policy, chỉ gửi signal tới PID mà systemd báo cho đúng unit lab.
- Lệnh dọn dẹp chỉ nhắm tới file/thư mục lab được tạo trong từng bài.

## Ý chính cần nắm

Unit file là bản khai báo để manager biết **chạy chương trình nào, ở thư mục nào, với môi trường nào, và xử lý process ra sao**. Unit không phải chính process; systemd đọc cấu hình rồi tạo và theo dõi process.

