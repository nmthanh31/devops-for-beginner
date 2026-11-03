# Bài 7 — UID/GID và Process Credentials

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Đọc UID/GID (real/effective) của process và biết kernel dùng nó để kiểm quyền.
> - Liên hệ với [L04 Identity & Permissions](../../domain4-Identity&Permissions/README.md).
>
> **Hình dung:** UID/GID là **thẻ nhân viên** process đeo — mọi cửa (file, port < 1024, signal) đều quẹt thẻ này.


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

<!-- learn:tail -->
## Tự kiểm tra

1. Lệnh xem UID/GID của PID 1234?
2. User thường có `kill` được process của root không?

<details>
<summary>Đáp án</summary>

1. `ps -o pid,user,uid,gid -p 1234` hoặc `grep -E 'Uid|Gid' /proc/1234/status`.
2. Không — gửi signal cần cùng UID (hoặc quyền đặc biệt).

</details>

