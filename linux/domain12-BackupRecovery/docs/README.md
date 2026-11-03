# L12 — Thứ tự học

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [Backup bảo vệ điều gì, tới đâu](./01-backup-design.md) | 35′ | Dữ liệu nào? Full/incr/diff? RPO/RTO? Failure domain? |
| 2 | [Nhất quán, kiểm tra, restore](./02-consistency-and-restore.md) | 35′ | tar/rsync/dd; checksum chứng minh gì; restore drill |
| 3 | [Runbook & evidence](./03-recovery-runbook.md) | 25′ | Runbook người khác chạy được; lỗi hay gặp |
| 4 | [Baseline, health, readiness, rollback](./04-health-baseline-and-rollback.md) | 40′ | 4 bề mặt kiểm service; vòng thay đổi an toàn; cold rebuild |
| — | [Lệnh cần nhớ](./00-command-reference.md) | — | Tra cứu |

Liên hệ [L05 storage/mount](../../domain5-Storage&Mounts/docs/README.md): backup đặt trên cùng disk/VM không bảo vệ được khi disk hoặc VM hỏng; mount sai có thể khiến backup đọc nhầm filesystem.
