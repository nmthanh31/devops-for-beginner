# Bài 10 — Thread và Process State

### Thread là gì?

Thread là một luồng thực thi bên trong process.

~~~text
Process
├── Thread 1
├── Thread 2
└── Thread 3
~~~

Các thread trong cùng process thường chia sẻ:

~~~text
memory/address space
open file descriptors
environment
credentials
~~~

Mỗi thread vẫn có execution context riêng.

### Process khác thread

Process thường có address space, FD table, credentials, environment và một hoặc nhiều thread.

~~~text
process ≠ thread
~~~

### Process state

| State | Ý nghĩa |
|---|---|
| R | Running hoặc runnable |
| S | Interruptible sleep |
| D | Uninterruptible sleep |
| T | Stopped |
| Z | Zombie |

Process tồn tại không có nghĩa nó đang dùng CPU. Ví dụ sleep thường ở trạng thái S trong phần lớn thời gian.

### Cần nhớ

1. Process có thể chứa nhiều thread.
2. Thread trong cùng process chia sẻ nhiều resource.
3. Process và thread là hai khái niệm khác nhau.
4. Process tồn tại không có nghĩa nó đang chạy CPU.
5. State cho biết process đang chạy, chờ, dừng hay zombie.

---

