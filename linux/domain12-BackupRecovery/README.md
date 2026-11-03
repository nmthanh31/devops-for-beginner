# L12 — Backup & Recovery

> **Câu hỏi domain này trả lời:** Dữ liệu nào phải bảo vệ, bản sao để ở đâu, và làm sao **chứng minh** service dùng được sau restore hoặc rollback?

**Mô hình cần nhớ một câu:** *Backup chưa restore thử thì chưa phải backup; hash chứng minh archive không đổi, chỉ app đọc được data mới chứng minh restore dùng được.*

## Học gì

1. [Lý thuyết (4 bài)](./docs/README.md)
2. [Lab: backup, verify, restore](./lab/01-backup-restore-hash.md)
3. Sau đó: [G-Linux gate W5](../weekly-labs/W5-linux-operations-gate.md)

## Đạt domain khi bạn có thể

- [ ] Phân loại dữ liệu service và chọn nơi lưu theo failure domain.
- [ ] Tính RPO/RTO thực tế từ một timeline.
- [ ] Backup → hash → restore staging → diff/stat → app test, có runbook.
- [ ] Kiểm service theo 4 bề mặt và rollback có verify.

## Liên kết

- Trước: [L11 SSH & Host Security](../domain11-SSHHostSecurity/README.md) · Tiếp theo: [Network N01–N12](../../network/README.md)

## Nguồn

[LPIC-2 V4.5 Objective 206.2](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5). Phần nhất quán ứng dụng, health/readiness và cold rebuild là mở rộng vận hành.
