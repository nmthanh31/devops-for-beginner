# Bài 2 — Process được tạo như thế nào?

### Mô hình cơ bản

~~~text
parent process
      │
      ├── fork()/clone()
      ▼
child process
      │
      └── exec()
          ▼
      program mới
~~~

Ví dụ:

~~~text
terminal
   └── bash
        └── sleep 300
~~~

Bash thường là parent của sleep.

### fork() và clone()

fork() hoặc clone() tạo process mới dựa trên process hiện tại.

Child có thể thừa hưởng từ parent:

- environment;
- working directory;
- file descriptors;
- credentials;
- một phần runtime state.

### exec()

exec() thay thế program đang chạy trong process bằng program khác.

Điểm quan trọng:

> exec() không nhất thiết tạo PID mới. Nó thay đổi program image của process hiện tại.

~~~text
bash
  │
  ├── fork()
  ▼
child process
  │
  ├── exec()
  ▼
sleep
~~~

### Cần nhớ

1. fork() hoặc clone() tạo child.
2. exec() thay program đang chạy trong process.
3. Parent và child có quan hệ trong process tree.
4. exec() không đồng nghĩa với tạo PID mới.

---

