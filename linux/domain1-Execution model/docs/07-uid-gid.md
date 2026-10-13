# Bài 7 — UID/GID và Process Credentials

### UID và GID

- UID: User ID, user mà process chạy dưới đó.
- GID: Group ID, group chính của process.

~~~text
UID = 1000
GID = 1000
~~~

### Kernel sử dụng credentials

Kernel dùng UID/GID khi process muốn:

- đọc hoặc ghi file;
- mở device;
- bind resource;
- gửi signal;
- truy cập tài nguyên hệ thống.

User đang login không nhất thiết là user của process.

Ví dụ service có thể chạy dưới:

~~~text
www-data
nginx
postgres
~~~

Câu hỏi đúng là:

> Process thực sự chạy với UID/GID nào?

### Cần nhớ

1. UID xác định user identity.
2. GID xác định group identity.
3. Kernel dùng UID/GID để kiểm tra quyền.
4. User login và process user có thể khác nhau.

---

