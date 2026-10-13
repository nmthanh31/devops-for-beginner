# Bài 9 — Process và TCP Socket

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

