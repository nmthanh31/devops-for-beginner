# Bài 1 — Program và Process

### Program là gì?

Program là chương trình được lưu trên disk.

Ví dụ:

~~~text
/usr/bin/python3
/usr/bin/nginx
/usr/bin/sleep
~~~

Khi chưa chạy, program chưa có:

- PID;
- memory runtime;
- environment runtime;
- file descriptor;
- process state.

### Process là gì?

Process là một instance đang chạy của program.

Khi chạy:

~~~bash
python3 app.py
~~~

Linux tạo một process để thực thi chương trình Python.

Process có runtime context riêng:

~~~text
Python process
├── PID
├── PPID
├── UID/GID
├── environment
├── working directory
├── memory
├── threads
├── file descriptors
└── signal handlers
~~~

> Program là chương trình trên disk. Process là phiên bản đang chạy của chương trình đó.

### Một program có thể tạo nhiều process

~~~text
/usr/bin/python3
        │
        ├── process PID 5012
        └── process PID 5078
~~~

Hai process có thể dùng cùng executable nhưng có PID, memory, environment, CWD, FD và state riêng.

### Cần nhớ

1. Program là file chương trình trên disk.
2. Process là instance đang chạy của program.
3. Một program có thể tạo nhiều process.
4. Mỗi process có runtime context riêng.

---

