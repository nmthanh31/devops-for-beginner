# Bài 8 — File Descriptor

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Giải thích FD là số đại diện cho tài nguyên đang mở (file, pipe, socket, terminal).
> - Dùng FD để trả lời: ai giữ file? ai giữ port? vì sao xóa file mà disk chưa free?
>
> **Hình dung:** FD là **số phiếu gửi đồ** ở quầy — process cầm phiếu số 3 để lấy đúng món (file/socket) kernel đang giữ hộ.


### FD là gì?

File Descriptor, viết tắt FD, là số nguyên đại diện cho resource mà process đang mở.

Process thao tác với file hoặc socket thông qua FD.

~~~text
process
   │
   └── FD table
~~~

### Ba FD tiêu chuẩn

~~~text
FD 0 → stdin
FD 1 → stdout
FD 2 → stderr
~~~

- stdin: đầu vào;
- stdout: đầu ra thông thường;
- stderr: lỗi.

### FD có thể trỏ tới nhiều resource

~~~text
FD 0 → terminal
FD 1 → log file
FD 2 → terminal
FD 3 → TCP socket
FD 4 → pipe
~~~

FD có thể đại diện cho:

~~~text
regular file
directory
terminal
pipe
socket
device
~~~

### Quá trình mở file

~~~text
file trên disk
      │
      ├── open()
      ▼
kernel open-file object
      │
      ▼
FD 3 của process
~~~

Child có thể kế thừa FD từ parent. Điều này giúp giải thích pipe, redirect, socket truyền giữa các process và file vẫn bị giữ sau khi parent tạo child.

### FD trong troubleshooting

FD giúp trả lời:

- Process nào đang giữ file?
- Port đang bị process nào chiếm?
- Socket nào đang mở?
- Vì sao file đã xóa nhưng disk chưa free?
- Vì sao filesystem chưa unmount được?

### Cần nhớ

1. FD là số đại diện cho resource đang mở.
2. 0, 1, 2 là stdin, stdout, stderr.
3. Socket, pipe và terminal cũng dùng FD.
4. FD là cầu nối giữa process và tài nguyên bên ngoài.

---

<!-- learn:tail -->
## Tự kiểm tra

1. Xem process 1234 đang mở những gì?
2. Vì sao `umount` báo busy?

<details>
<summary>Đáp án</summary>

1. `ls -l /proc/1234/fd` hoặc `lsof -p 1234`.
2. Một process còn giữ FD (hoặc CWD) trên filesystem đó — tìm bằng `lsof +f -- MOUNT`/`fuser -vm`.

</details>

