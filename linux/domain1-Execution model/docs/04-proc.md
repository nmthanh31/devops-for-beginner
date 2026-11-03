# Bài 4 — /proc — Cửa sổ nhìn vào process

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Dùng `/proc/PID/` để đọc trực tiếp status, cmdline, exe, cwd, environ, fd của process.
> - Hiểu `/proc` là giao diện kernel, không phải file trên disk.
>
> **Hình dung:** `/proc/PID` là **hồ sơ bệnh án sống** của process — kernel cập nhật tức thì mỗi lần bạn đọc.


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

<!-- learn:tail -->
## Tự kiểm tra

1. Xem process đang ở thư mục nào?
2. Vì sao đọc `/proc/PID/environ` của process user khác bị từ chối?

<details>
<summary>Đáp án</summary>

1. `readlink /proc/PID/cwd`.
2. Environment có thể chứa secret — chỉ owner/root đọc được.

</details>

