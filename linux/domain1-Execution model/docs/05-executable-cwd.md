# Bài 5 — Executable và CWD

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Biết process đang chạy binary nào (`/proc/PID/exe`) và đứng ở thư mục nào (CWD).
> - Giải thích vì sao relative path trong app/service hỏng khi CWD khác.
>
> **Hình dung:** CWD là **chỗ đứng** của người nấu. Công thức ghi "lấy muối ở kệ bên trái" (relative path) chỉ đúng nếu đứng đúng chỗ.


### Executable

Executable là program mà process đang chạy.

~~~text
program trên disk
       │
       ├── exec()
       ▼
process đang chạy
~~~

### CWD

CWD là Current Working Directory, tức thư mục làm việc hiện tại của process.

Executable và CWD là hai khái niệm khác nhau:

~~~text
executable = /usr/bin/python3
CWD        = /opt/my-app
~~~

### Relative path

Với code:

~~~python
open("config.yaml")
~~~

File thường được tìm từ CWD:

~~~text
/opt/my-app/config.yaml
~~~

Nếu CWD thay đổi, application có thể đọc file khác hoặc không tìm thấy file.

Vì vậy một application có thể:

~~~text
chạy bằng tay   → thành công
chạy bởi service → thất bại
~~~

chỉ vì CWD khác nhau.

### Cần nhớ

1. Executable là chương trình process đang chạy.
2. CWD là thư mục làm việc của process.
3. Relative path thường được resolve từ CWD.
4. CWD khác nhau có thể làm application hoạt động khác nhau.

---

<!-- learn:tail -->
## Tự kiểm tra

1. Script đọc `config.yaml` chạy tay OK, chạy bằng systemd lỗi `No such file`. Nghi gì?
2. `which python3` và `/proc/PID/exe` có thể khác nhau không?

<details>
<summary>Đáp án</summary>

1. CWD khác — systemd mặc định CWD là `/`; đặt `WorkingDirectory=` hoặc dùng absolute path.
2. Có — process có thể chạy từ path khác/venv, hoặc symlink trỏ tới binary thật.

</details>

