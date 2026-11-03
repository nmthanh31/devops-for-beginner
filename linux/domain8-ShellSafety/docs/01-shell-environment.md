# Bài 1 — Shell, command và environment

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Phân biệt shell variable và environment variable (được child kế thừa).
> - Biết `PATH` quyết định command nào được chạy; profile vs `.bashrc` nạp khi nào.
>
> **Liên hệ:** [L01 environment](../../domain1-Execution%20model/docs/06-environment.md) — env là thuộc tính của process.


## Shell là gì?

Shell là chương trình nhận lệnh, phân tích lệnh rồi khởi chạy command. Bash là một shell phổ biến và là shell được LPIC-1 giả định trong phần command line.

```text
người dùng gõ lệnh → Bash phân tích → Bash gọi program → program trả kết quả
```

## Environment là gì?

Environment là tập các biến được truyền cho process con. Ví dụ `PATH`, `HOME`, `LANG` hoặc biến ứng dụng.

Một shell con thường nhận bản sao environment từ shell cha. Thay đổi trong shell con không tự quay ngược làm thay đổi shell cha.

## PATH

`PATH` là danh sách thư mục shell tìm executable. Khi gọi một command không có `/`, shell tìm lần lượt trong các thư mục của `PATH`.

Đừng thêm thư mục không tin cậy vào đầu `PATH`, đặc biệt là thư mục hiện tại. Có thể khiến shell chạy nhầm file cùng tên.

## Profile và `.bashrc`

Shell có thể đọc file cấu hình theo kiểu shell và cách đăng nhập. Các file thường gặp gồm `/etc/profile`, `/etc/bash.bashrc`, `~/.profile` và `~/.bashrc` tùy distribution.

`source file` đọc lại nội dung file trong shell hiện tại; nó không tạo process shell mới.

## Function và alias

Function gom nhiều lệnh thành một command có tên. Alias thường dùng cho shortcut tương tác. Không nên dùng alias để che giấu hành vi nguy hiểm trong script; script nên gọi command rõ ràng và predictable.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`VAR=x` là script con thấy được." | Cần `export VAR`. |
| "Alias dùng được trong script." | Script không nạp alias của shell tương tác. |
| "Thêm `.` vào PATH cho tiện." | Rủi ro chạy nhầm file độc trong thư mục hiện tại. |

## Tự kiểm tra

1. `A=1; bash -c 'echo $A'` in gì? Còn `export A=1; bash -c 'echo $A'`?
2. Sửa `~/.bashrc` xong, phiên hiện tại chưa thấy thay đổi. Làm gì?

<details>
<summary>Đáp án</summary>

1. Dòng trống; rồi `1`.
2. `source ~/.bashrc` hoặc mở shell mới.

</details>

## Nguồn

- [LPIC-1 103.1/105.1 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

