# Bài 11 — Signal

### Signal là gì?

Signal là cơ chế kernel dùng để gửi thông báo hoặc yêu cầu tới process.

~~~text
SIGTERM = 15
SIGKILL = 9
SIGINT  = 2
SIGHUP  = 1
~~~

### SIGTERM

SIGTERM yêu cầu process kết thúc có trật tự:

~~~text
process nhận SIGTERM
        ↓
xử lý signal
        ↓
cleanup
        ↓
exit
~~~

Application có thể đóng file, đóng socket, flush dữ liệu, hoàn tất request, ghi log và giải phóng tài nguyên.

### SIGKILL

SIGKILL yêu cầu kernel terminate process ngay lập tức.

Process không thể:

- catch SIGKILL;
- ignore SIGKILL;
- cài handler cho SIGKILL;
- cleanup sau SIGKILL.

### Các signal khác

- SIGINT thường được gửi khi nhấn Ctrl+C.
- SIGHUP thường liên quan đến terminal hoặc session bị đóng. Một số daemon dùng nó để reload configuration.

### Vì sao ưu tiên SIGTERM?

~~~text
gửi SIGTERM
    ↓
chờ process tự cleanup
    ↓
nếu không phản hồi mới dùng SIGKILL
~~~

Dùng SIGKILL ngay có thể làm mất dữ liệu, cắt request, không flush file, đóng socket đột ngột và bỏ qua cleanup.

### Cần nhớ

1. Signal là event hoặc request gửi tới process.
2. SIGTERM cho process cơ hội cleanup.
3. SIGKILL do kernel terminate trực tiếp.
4. SIGKILL không thể bị catch hoặc ignore.
5. Không nên dùng SIGKILL như lựa chọn đầu tiên.

---

