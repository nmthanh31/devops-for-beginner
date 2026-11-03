# L01 — Execution Model

> **Câu hỏi domain này trả lời:** Nhìn vào một process bất kỳ — nó chạy program nào, ai tạo ra nó, chạy dưới ai, đứng ở đâu, mang env gì, mở file/socket nào, đang ở state nào, và kết thúc ra sao?

**Mô hình cần nhớ một câu:** *Program được `fork`+`exec` thành process; process mang PID/PPID, UID/GID, CWD, env, FD (gồm socket), state — và `/proc/PID` cho bạn nhìn thấy tất cả.*

```text
program ──exec()──► process
                    ├── PID / PPID          (Bài 3)
                    ├── UID / GID           (Bài 7)
                    ├── CWD, executable     (Bài 5)
                    ├── environment         (Bài 6)
                    ├── threads, state      (Bài 10)
                    ├── file descriptors    (Bài 8) ── socket (Bài 9)
                    ├── signal handling     (Bài 11)
                    └── exit status         (Bài 12)
```

## Lộ trình

| # | Bài | Thời lượng |
|---|---|---|
| 1–3 | [Program/process](./docs/01-program-process.md) · [Tạo process](./docs/02-process-creation.md) · [PID/PPID/tree](./docs/03-pid-ppid-process-tree.md) | 45′ |
| 4–6 | [/proc](./docs/04-proc.md) · [Executable & CWD](./docs/05-executable-cwd.md) · [Environment](./docs/06-environment.md) ([lệnh env](./docs/06-environment-commands.md)) | 45′ |
| 7–9 | [UID/GID](./docs/07-uid-gid.md) · [File descriptor](./docs/08-file-descriptor.md) · [TCP socket](./docs/09-tcp-socket.md) | 45′ |
| 10–12 | [Thread & state](./docs/10-thread-process-state.md) · [Signal](./docs/11-signal.md) · [Exit code](./docs/12-exit-code.md) | 45′ |
| 13 | [Tổng hợp & quy trình troubleshoot](./docs/13-summary-execution-model.md) | 20′ |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) · [Pass gate (có đáp án)](./docs/README.md#pass-gate) | — |

## Lab

[Danh sách lab](./lab/README.md): SIGTERM vs SIGKILL · bài độc lập execution model.

## Đạt domain khi bạn có thể

- [ ] Với một PID bất kỳ, trả lời đủ 10 câu ở [mục tiêu](./docs/README.md#mục-tiêu) bằng `ps`/`pstree`/`/proc`/`lsof`/`ss`.
- [ ] Map một port LISTEN → PID → FD → binary → user.
- [ ] Chứng minh khác biệt TERM vs KILL bằng exit code và cleanup.
- [ ] Đọc exit code `128+N`.

## Liên kết

- Tiếp theo: [L02 Boot & Service](../domain2-Boot&Service/README.md)
