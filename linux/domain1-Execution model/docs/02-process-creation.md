# Bài 2 — Process được tạo như thế nào?

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Mô tả chuỗi `fork()` (nhân bản process) → `exec()` (thay chương trình) → `wait()`.
> - Biết child kế thừa gì từ parent (env, CWD, FD, credentials).
>
> **Hình dung:** `fork()` là **photocopy** cả người nấu lẫn căn bếp; `exec()` là bản sao **vứt công thức cũ, cầm công thức mới** — vẫn bếp đó, vẫn đồ nghề đó (FD, env, CWD).


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

<!-- learn:tail -->
## Tự kiểm tra

1. Sau `exec()`, PID có đổi không?
2. Vì sao redirect `cmd > out.txt` hoạt động?

<details>
<summary>Đáp án</summary>

1. Không — cùng process, chỉ thay chương trình.
2. Shell fork, trong child mở `out.txt` làm FD 1, rồi exec `cmd` — `cmd` kế thừa FD 1.

</details>

