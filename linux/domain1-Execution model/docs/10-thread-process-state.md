# Bài 10 — Thread và Process State

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Phân biệt process và thread (chia sẻ memory, FD).
> - Đọc state `R`, `S`, `D`, `T`, `Z` và biết state nào đáng lo.
>
> **Hình dung:** process là **một căn bếp**; thread là **nhiều đầu bếp** trong cùng bếp, dùng chung nồi niêu.


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

<!-- learn:tail -->
## Tự kiểm tra

1. Nhiều process `D` cùng lúc gợi ý gì?
2. Có `kill -9` được process `Z` không?

<details>
<summary>Đáp án</summary>

1. Đang chờ I/O kernel (disk/NFS chậm) — xem [L09](../../domain9-ResourceTroubleshooting/docs/04-disk-io.md).
2. Không cần/không được — nó đã chết; parent phải `wait()` (hoặc parent chết để PID 1 thu dọn).

</details>

