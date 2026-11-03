# L08 — Shell Safety & Bash Automation

> **Câu hỏi domain này trả lời:** Làm sao viết script Bash chạy **dự đoán được** — không vỡ vì khoảng trắng, không xóa nhầm, báo lỗi bằng exit code có nghĩa và tự dọn dẹp?

**Mô hình cần nhớ một câu:** *Quote mọi biến, validate input trước khi ghi/xóa, kiểm exit status (cả pipeline), dọn bằng `trap` — script an toàn không chỉ là script chạy được.*

```text
input → parse/quote → command → exit status → decision → output/cleanup
```

## Lộ trình

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [Shell & environment](./docs/01-shell-environment.md) | 20′ | export, PATH, profile vs bashrc |
| 2 | [Quoting & expansion](./docs/02-quoting-expansion-safety.md) | 30′ | Vì sao `"$var"` |
| 3 | [Exit status, điều kiện, pipeline](./docs/03-exit-status-conditionals-pipelines.md) | 30′ | `pipefail`, `&&`/`||`, redirect |
| 4 | [Input validation & file safety](./docs/04-input-validation-file-safety.md) | 30′ | Chặn xóa nguy hiểm, mktemp, find |
| 5 | [Cấu trúc, cleanup, trap](./docs/05-script-structure-cleanup.md) | 30′ | Khung script, idempotency |
| 6 | [Debug & ShellCheck](./docs/06-debugging-and-shellcheck.md) | 20′ | `bash -x`, ShellCheck |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) | — | — |

## Lab

[Danh sách lab](./lab/README.md): safe file report · fault & repair · **diagnose.sh + 8 test**.

## Đạt domain khi bạn có thể

- [ ] Viết `diagnose.sh` với exit code phân biệt lớp lỗi, 8 test PASS, ShellCheck sạch.
- [ ] Giải thích và tránh word splitting, glob, `rm -rf "$EMPTY/"*`.
- [ ] Dùng `set -Eeuo pipefail` và biết giới hạn của nó.
- [ ] Script không in secret, tự dọn file tạm.

## Liên kết

- Trước: [L07](../domain7-LogsTimeTimers/README.md) · Tiếp theo: [L09 Resource Troubleshooting](../domain9-ResourceTroubleshooting/README.md)

## Nguồn

LPIC-1 [103.1, 103.3, 103.4, 105.1, 105.2](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0) · [ShellCheck](https://www.shellcheck.net/)
