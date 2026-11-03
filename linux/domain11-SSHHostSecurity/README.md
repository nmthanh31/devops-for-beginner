# L11 — SSH & Host Security

> **Câu hỏi domain này trả lời:** Làm sao đăng nhập từ xa an toàn bằng key, kiểm soát những gì đang mở ra mạng, và thay đổi firewall mà không tự khóa mình?

**Mô hình cần nhớ một câu:** *Host key xác thực server, user key xác thực người; listener, firewall và sshd policy là ba lớp độc lập — luôn test bằng phiên mới và giữ đường phục hồi.*

## Học gì

1. [Lý thuyết (3 bài)](./docs/README.md)
2. [Lab: SSH key và host firewall](./lab/01-ssh-key-and-host-firewall.md)

## Đạt domain khi bạn có thể

- [ ] Thiết lập key-only login từ Windows, có `ssh -v` + journal làm evidence.
- [ ] Phân loại lỗi SSH theo giai đoạn (resolve / timeout / refused / host key / publickey).
- [ ] Đọc `sshd -T -C` để biết config hiệu lực.
- [ ] Bật host firewall với allowlist SSH mà không mất phiên; có positive + negative test và rollback.

## Liên kết

- Trước: [L10 Host Networking](../domain10-HostNetworking/README.md) · Tiếp theo: [L12 Backup & Recovery](../domain12-BackupRecovery/README.md)

## Nguồn

[LPIC-1 Topic 110](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0) · [LPIC-2 212.3](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5) · [Ubuntu Server firewall](https://ubuntu.com/server/docs/firewalls/)
