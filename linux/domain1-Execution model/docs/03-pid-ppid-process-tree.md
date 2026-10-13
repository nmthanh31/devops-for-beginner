# Bài 3 — PID, PPID và Process Tree

### PID

PID là Process ID, định danh của process.

~~~text
PID = 4210
~~~

PID giúp ta chọn đúng process để quan sát, kiểm tra hoặc gửi signal.

### PPID

PPID là Parent Process ID.

~~~text
PID  = 4210
PPID = 3900
~~~

Process 3900 là parent của process 4210.

### Process tree

~~~text
bash(1000)
 ├── sleep(1100)
 └── python(1200)
      └── worker(1300)
~~~

- Parent: process trực tiếp tạo process hiện tại.
- Child: process được tạo bởi process hiện tại.
- Ancestor: process tổ tiên nằm phía trên trong cây.

Nếu parent chết trước child, child có thể được re-parent cho PID 1 hoặc một subreaper.

### Cần nhớ

1. PID định danh process hiện tại.
2. PPID cho biết parent trực tiếp.
3. Process tree thể hiện quan hệ parent-child.
4. Process không tồn tại hoàn toàn độc lập.
5. Parent chết không nhất thiết làm child chết ngay.

---

