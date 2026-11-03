# Bài 3 — Exit status, điều kiện và pipeline

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Dùng exit status (0 = thành công) để rẽ nhánh với `if`, `&&`, `||`.
> - Biết exit status của pipeline mặc định là của **lệnh cuối** và cách dùng `pipefail`.
> - Tách stdout và stderr.


## Exit status là gì?

Mỗi command trả về một mã kết thúc. Theo quy ước:

```text
0     = thành công
khác 0 = lỗi hoặc điều kiện không thành công
```

Đây là dữ liệu để script quyết định, không phải chỉ là thông tin hiển thị.

`$?` chứa exit status của command gần nhất; phải đọc nó ngay nếu cần vì command tiếp theo sẽ thay đổi giá trị này.

## `&&` và `||`

```text
A && B  = chạy B nếu A thành công
A || B  = chạy B nếu A thất bại
```

Đừng đọc `||` như “bắt mọi lỗi” một cách máy móc; một số command dùng exit status khác 0 cho kết quả hợp lệ nhưng không tìm thấy dữ liệu.

## `if` và `test`

`if` kiểm tra exit status của command. `test` hoặc cú pháp `[` kiểm tra file, string, số và điều kiện khác.

Ví dụ tư duy:

```text
kiểm tra path tồn tại → nếu đúng thì đọc → nếu sai thì báo lỗi và dừng
```

## Pipeline

Pipeline nối stdout của command trước vào stdin của command sau:

```text
producer | filter | formatter
```

Mặc định exit status của pipeline thường là status của command cuối. Vì vậy command đầu có thể lỗi nhưng pipeline vẫn trông như thành công. Bash có `pipefail` để pipeline phản ánh lỗi của các thành phần phù hợp hơn.

## stdout và stderr

- File descriptor `1`: stdout.
- File descriptor `2`: stderr.

Redirect stdout không tự redirect stderr. Khi debug, cần biết output đang đi đâu.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`cmd1 | cmd2` fail nếu cmd1 fail." | Mặc định chỉ lấy exit của cmd2 — dùng `set -o pipefail`. |
| "`a && b || c` giống if/else." | Nếu `b` fail thì `c` cũng chạy. |
| "`> file 2>&1` và `2>&1 > file` như nhau." | Thứ tự redirect quan trọng; cái sau chỉ đưa stdout vào file. |

## Tự kiểm tra

1. `grep foo missing.txt | wc -l; echo $?` in exit code của ai?
2. Ghi cả stdout và stderr vào `out.log`?

<details>
<summary>Đáp án</summary>

1. Của `wc` (thường 0) — lỗi của `grep` bị che.
2. `cmd > out.log 2>&1` (hoặc `&> out.log` trong Bash).

</details>

## Nguồn

- [LPIC-1 103.4/105.2 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

