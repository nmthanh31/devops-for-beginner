# Bài 13 — Tổng hợp Execution Model

### Sơ đồ tổng thể

~~~text
                    ┌──────────────┐
                    │   PROGRAM    │
                    │ executable   │
                    └──────┬───────┘
                           │
                          exec()
                           │
                           ▼
                 ┌───────────────────┐
                 │      PROCESS      │
                 │                   │
                 │ PID / PPID        │
                 │ UID / GID         │
                 │ Environment       │
                 │ CWD               │
                 │ Memory            │
                 │ Threads           │
                 │ FD Table          │
                 │ Signal handling   │
                 └────────┬──────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
           Files        Pipes        Sockets
             │                          │
             ▼                          ▼
          storage                    network
                          │
                          ▼
                    signal / exit
                          │
                          ▼
                       EXIT CODE
~~~

### Chuỗi tạo process

~~~text
bash
  ↓
fork/clone
  ↓
child process
  ↓
exec python
  ↓
Python process
  ├── PID/PPID
  ├── UID/GID
  ├── CWD
  ├── environment
  ├── threads
  └── FD table
        ├── terminal
        ├── files
        ├── pipes
        └── TCP socket
  ↓
SIGTERM hoặc normal exit
  ↓
exit status
~~~

### /proc quan sát những gì?

| Thành phần | Nơi quan sát |
|---|---|
| Command line | /proc/<PID>/cmdline |
| Executable | /proc/<PID>/exe |
| CWD | /proc/<PID>/cwd |
| Environment | /proc/<PID>/environ |
| PID, PPID, UID, GID, state | /proc/<PID>/status |
| File và socket | /proc/<PID>/fd/ |
| Thread | /proc/<PID>/task/ |

### Quy trình troubleshoot process

~~~text
process có tồn tại không?
        ↓
program nào đang chạy?
        ↓
PID và PPID là gì?
        ↓
process chạy dưới UID/GID nào?
        ↓
CWD là gì?
        ↓
environment có đúng không?
        ↓
process đang ở state nào?
        ↓
process giữ FD nào?
        ↓
có socket không?
        ↓
đang listen ở address/port nào?
        ↓
nếu gửi SIGTERM thì xử lý ra sao?
        ↓
exit code là gì?
~~~

---

