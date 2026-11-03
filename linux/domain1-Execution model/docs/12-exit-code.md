# Bài 12 — Exit Code

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Đọc exit code (0 = thành công, khác 0 = lỗi) và quy ước `128 + N` khi chết vì signal N.
> - Dùng exit code trong script và khi đọc `systemctl status`.
>
> **Hình dung:** exit code là **tờ biên bản cuối ca** process để lại cho parent.


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

<!-- learn:tail -->
## Tự kiểm tra

1. Exit code 137 nghĩa gì?
2. Exit code 143?

<details>
<summary>Đáp án</summary>

1. 128 + 9 → bị SIGKILL (thường OOM kill hoặc `kill -9`).
2. 128 + 15 → bị SIGTERM.

</details>

