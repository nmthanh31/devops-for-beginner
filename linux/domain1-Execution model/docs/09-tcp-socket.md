# Bài 9 — Process và TCP Socket

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Nối được chuỗi process → FD → socket → `IP:port` LISTEN.
> - Trả lời "port 8080 do process nào giữ?" bằng `ss -lntp`.
>
> **Hình dung:** listening socket là **quầy tiếp nhận** mở ở một địa chỉ + số cửa; process là nhân viên ngồi quầy, FD là chìa khóa quầy.


### Socket là gì?

Socket là endpoint dùng để giao tiếp.

TCP server thường bind socket vào:

~~~text
IP address + port
~~~

Ví dụ:

~~~text
0.0.0.0:8080
127.0.0.1:8080
~~~

### Chuỗi process đến listener

~~~text
program
   ↓
process
   ↓
file descriptor
   ↓
socket
   ↓
TCP listener
   ↓
IP:port
~~~

Ví dụ:

~~~text
/usr/bin/python3
        ↓
process PID 4210
        ↓
FD 3
        ↓
TCP socket
        ↓
LISTEN :8080
~~~

127.0.0.1 thường chỉ nhận kết nối local. 0.0.0.0 thường lắng nghe trên mọi IPv4 interface.

Port đang LISTEN chưa chắc client bên ngoài đã truy cập được.

### Quy trình troubleshoot port

~~~text
process có tồn tại không?
        ↓
process có socket không?
        ↓
socket có LISTEN không?
        ↓
bind address là gì?
        ↓
network path có vấn đề gì?
~~~

### Cần nhớ

1. Socket được process sử dụng qua FD.
2. TCP listener liên hệ process với port.
3. Cần biết cả port và bind address.
4. Port LISTEN không tự động đảm bảo truy cập được.

---

<!-- learn:tail -->
## Tự kiểm tra

1. `ss -lntp` thấy `users:(("python3",pid=812,fd=3))`. `fd=3` nghĩa là gì?
2. Port 8080 báo `Address already in use`. Tìm thủ phạm?

<details>
<summary>Đáp án</summary>

1. Socket listen là FD số 3 của PID 812 — thấy được trong `/proc/812/fd/3` (`socket:[inode]`).
2. `sudo ss -lntp 'sport = :8080'`.

</details>

