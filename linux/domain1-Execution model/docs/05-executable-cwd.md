# Bài 5 — Executable và CWD

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

