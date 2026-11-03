# Linux L01–L12

12 domain, học trong 3 tuần (W3–W5). Mỗi domain trả lời một câu hỏi về **một Linux host**; domain sau dùng lại cơ chế của domain trước. Sau Linux là [Network N01–N12](../network/README.md).

## Bản đồ: một service "không chạy" chạm tới những domain nào

```text
Service không phục vụ được
   ├─ Boot tới đâu? unit có được kích hoạt?         L02 Boot & Service
   ├─ Process nào, PID/UID/CWD/env/FD/state?         L01 Execution model
   ├─ Config/data/log nằm đâu, path đúng không?      L03 Filesystem & Path
   ├─ Process có quyền đọc/ghi không?                L04 Identity & Permissions
   ├─ Disk mount đúng chưa, còn bytes/inode?         L05 Storage & Mounts
   ├─ Đúng version package, config còn đó?           L06 Package Lifecycle
   ├─ Log nói gì, giờ có đúng, job định kỳ có chạy?  L07 Logs, Time & Timers
   ├─ Script chẩn đoán/tự động có an toàn?           L08 Shell Safety
   ├─ CPU / memory / I/O có nghẽn?                   L09 Resource Troubleshooting
   ├─ IP/route/DNS/socket tới được không?            L10 Host Networking
   ├─ Truy cập từ xa an toàn, firewall đúng?         L11 SSH & Host Security
   └─ Hỏng rồi — restore và rollback thế nào?        L12 Backup & Recovery
```

## Lịch học

### W3 — Linux core · 12–18/10/2026

| Domain | Câu hỏi chính |
|---|---|
| [L01 Execution model](./domain1-Execution%20model/README.md) | Process là gì và mang theo những gì? |
| [L02 Boot & Service](./domain2-Boot&Service/README.md) | Từ nút nguồn tới service phục vụ traffic |
| [L03 Filesystem & Path](./domain3-Filesystem&Path/README.md) | Path → inode; link; file đã xóa vẫn chiếm chỗ |
| [L04 Identity & Permissions](./domain4-Identity&Permissions/README.md) | Process là ai, có đi qua được path không? |

Lab journal tuần: [lab-journal/](./lab-journal/README.md).

### W4 — Data & automation · 19–25/10/2026

| Domain | Câu hỏi chính |
|---|---|
| [L05 Storage & Mounts](./domain5-Storage&Mounts/README.md) | Disk → FS → mount bền vững; đầy bytes hay inode? |
| [L06 Package Lifecycle](./domain6-PackageLifecycle/README.md) | Cài/verify/hold/rollback có kiểm soát |
| [L07 Logs, Time & Timers](./domain7-LogsTimeTimers/README.md) | Lọc log, clock đúng, job thật sự thành công |
| [L08 Shell Safety](./domain8-ShellSafety/README.md) | Script dự đoán được, exit code có nghĩa |

### W5 — Linux operations gate · 26/10–01/11/2026

| Domain | Câu hỏi chính |
|---|---|
| [L09 Resource Troubleshooting](./domain9-ResourceTroubleshooting/README.md) | CPU, memory hay I/O? |
| [L10 Host Networking](./domain10-HostNetworking/README.md) | Tên → IP → route → socket |
| [L11 SSH & Host Security](./domain11-SSHHostSecurity/README.md) | Key-only, firewall không tự khóa |
| [L12 Backup & Recovery](./domain12-BackupRecovery/README.md) | Backup đã restore thử mới là backup |

Gate tuần: [G-Linux — W5 operations gate](./weekly-labs/W5-linux-operations-gate.md) (8 fault phủ ≥ 8/12 domain; đúng ≥ 7, sửa ≥ 6; không `777`, reboot hay restart mù).

## Cách học một domain

| Phần | Làm gì |
|---|---|
| `README.md` của domain | Câu hỏi chính, mô hình một câu, lộ trình có thời lượng, checklist "đạt domain" |
| `docs/0X-*.md` | Mỗi bài mở bằng **mục tiêu + hình dung**, kết bằng **hiểu lầm thường gặp + tự kiểm tra (đáp án ẩn)** |
| `docs/00-command-reference.md` | Tra cứu lệnh theo câu hỏi |
| `lab/` | Dự đoán → chạy → so "kết quả mong đợi" → Definition of Done → cleanup |

Luật PASS (theo roadmap): *prediction → baseline → one change → evidence ≥ 2 lớp → giải thích nhân quả → sửa tối thiểu → positive + negative verify → cleanup.*
