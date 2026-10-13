# Bài 4 — /proc — Cửa sổ nhìn vào process

### /proc là gì?

Linux expose runtime state của process qua:

~~~text
/proc/<PID>/
~~~

/proc là một pseudo-filesystem, không phải thư mục bình thường chứa file vật lý trên disk.

~~~text
process
   │
   └── kernel
         │
         └── /proc/<PID>
~~~

### Các entry quan trọng

| Đường dẫn | Ý nghĩa |
|---|---|
| /proc/<PID>/cmdline | Command line |
| /proc/<PID>/status | PID, PPID, state, UID, GID |
| /proc/<PID>/environ | Environment |
| /proc/<PID>/cwd | Working directory |
| /proc/<PID>/exe | Executable |
| /proc/<PID>/fd/ | File descriptors |
| /proc/<PID>/task/ | Threads |

### Vì sao /proc quan trọng?

/proc cung cấp evidence trực tiếp từ kernel để kiểm tra:

- executable thực tế;
- CWD thực tế;
- environment thực tế;
- UID/GID thực tế;
- FD thực tế;
- state thực tế.

> /proc/<PID> không phải folder chứa process. Nó là giao diện quan sát runtime state.

---

