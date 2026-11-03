# Bài 6 — Environment Variables

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Phân biệt shell variable và environment variable; biết env được **copy** sang child lúc tạo.
> - Đọc env của một process đang chạy và nhận diện rủi ro lộ secret.
>
> **Hình dung:** env là **túi đồ cá nhân** cha mẹ chuẩn bị cho con trước khi ra đi — đưa xong thì đổi túi của cha mẹ không ảnh hưởng con nữa.


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

<!-- learn:tail -->
## Tự kiểm tra

1. Đổi `export X=2` trong shell, service đã chạy trước đó thấy giá trị mới không?
2. Vì sao không nên truyền password qua env khi có thể tránh?

<details>
<summary>Đáp án</summary>

1. Không — env được copy lúc tạo process; phải restart.
2. Lộ qua `/proc/PID/environ`, log crash, child process kế thừa.

</details>

