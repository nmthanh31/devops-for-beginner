# Bài 12 — Exit Code

### Exit code là gì?

Khi process kết thúc, nó trả về exit code hoặc exit status.

~~~text
0        thành công
non-zero thất bại hoặc trạng thái đặc biệt
~~~

### Exit code phụ thuộc program

Mỗi program có thể định nghĩa exit code riêng.

Ví dụ grep có thể dùng:

~~~text
0 → tìm thấy pattern
1 → không tìm thấy pattern
2 → có lỗi khi thực hiện
~~~

### Exit code và signal

Nếu process bị signal terminate, shell thường biểu diễn bằng:

~~~text
128 + số signal
~~~

Ví dụ:

~~~text
SIGTERM (15) → 143
SIGKILL (9)  → 137
~~~

Nếu chương trình bắt SIGTERM rồi tự gọi exit(0), exit code có thể là 0.

### Vì sao exit code quan trọng?

Exit code được dùng bởi:

- shell script;
- automation;
- CI/CD;
- cron;
- service manager;
- health check;
- monitoring.

### Cần nhớ

1. Exit code là kết quả cuối cùng của process.
2. 0 thường có nghĩa thành công.
3. Non-zero thường biểu thị lỗi hoặc trạng thái đặc biệt.
4. Ý nghĩa chính xác phụ thuộc program.
5. Process bị signal terminate có thể có exit status đặc biệt.

---

