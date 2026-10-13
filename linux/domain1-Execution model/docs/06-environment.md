# Bài 6 — Environment Variables

### Environment là gì?

Environment là tập biến được truyền vào process.

~~~text
APP_ENV=production
PORT=8080
PATH=/usr/bin:/bin
HOME=/home/thanh
~~~

### Environment được truyền xuống child

~~~text
parent process
    ENV:
        APP_ENV=production
        PORT=8080
          │
          └── child process
                  ENV:
                      APP_ENV=production
                      PORT=8080
~~~

### Shell variable khác environment variable

~~~text
shell variable
      ≠
environment variable
~~~

Một biến chỉ tồn tại trong shell hiện tại chưa chắc được truyền cho child.

Muốn đưa biến vào environment, dùng export:

~~~bash
export APP_ENV=production
~~~

Mỗi process có environment riêng tại thời điểm nó được tạo. Thay đổi environment trong shell sau đó không tự động thay đổi environment của child đang chạy.

### Rủi ro bảo mật

Environment có thể chứa password, API key hoặc token. Đây không phải dữ liệu “vô hình”; process inspection có thể làm lộ chúng tùy quyền truy cập.

### Cần nhớ

1. Environment là runtime context của process.
2. Child thường nhận environment từ parent.
3. Shell variable không tự động là environment variable.
4. export đưa biến vào environment.
5. Secret trong environment vẫn có thể bị quan sát.

---

