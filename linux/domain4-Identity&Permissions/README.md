# L04 — Identity & Permissions

> **Câu hỏi domain này trả lời:** Khi process truy cập file — process là ai, file thuộc về ai, và process có đi qua được từng thư mục trên path không?

**Mô hình cần nhớ một câu:** *Kernel so UID/GID của **process** với owner/group/mode (+ACL) của **từng** component trên path; chọn một class rồi quyết định — sửa đúng identity và đúng path, không bao giờ 777.*

```text
process credentials (UID + GIDs) → x trên từng parent dir → owner/group/mode (+ACL) của inode cuối → allow/deny
```

## Lộ trình

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [User, group, identity](./docs/01-users-groups-identity.md) | 30′ | UID/GID của process; `id`, `getent` |
| 2 | [Ownership & rwx](./docs/02-ownership-and-rwx.md) | 35′ | rwx trên file vs directory; class nào được chọn |
| 3 | [umask & special bits](./docs/03-umask-special-bits.md) | 30′ | Mode mặc định; SUID/SGID/sticky |
| 4 | [Access check & chẩn đoán](./docs/04-access-check-troubleshooting.md) | 30′ | Checklist `Permission denied` |
| 5 | [sudo, PAM, ACL](./docs/05-sudo-pam-acl.md) | 30′ | `sudo -l`, luồng PAM, `getfacl`/mask |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) · [Ranh giới LPIC](./docs/README.md) | — | — |
| Lab | [Least privilege service, 4 fault](./lab/01-least-privilege-service.md) | 75′ | Sửa lỗi quyền không dùng 777 |

## Đạt domain khi bạn có thể

- [ ] Chạy một service dưới service account với quyền tối thiểu (đọc config, ghi data).
- [ ] Chẩn đoán `Permission denied` bằng `ps`/`id`/`namei -l`/`stat`/`getfacl`.
- [ ] Tính mode từ umask; nhận diện SUID/SGID/sticky.
- [ ] Luôn có negative test chứng minh user khác bị từ chối.

## Liên kết

- Trước: [L03 Filesystem & Path](../domain3-Filesystem&Path/README.md) · Tiếp theo: [L05 Storage & Mounts](../domain5-Storage&Mounts/README.md)
