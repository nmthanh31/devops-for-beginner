# Bài 6 — Debug và ShellCheck

## Debug bằng Bash

Khi script sai, cần biết shell đã thực sự chạy command nào và biến có giá trị gì. Bash tracing có thể giúp nhìn execution flow, nhưng phải cẩn thận vì trace có thể làm lộ secret.

Không bật trace bừa bãi trong script chứa password, token hoặc key.

## ShellCheck

ShellCheck là công cụ phân tích tĩnh cho shell script. Nó có thể phát hiện nhiều lỗi phổ biến như:

- Quên quote biến.
- Dùng test sai.
- Expansion nguy hiểm.
- So sánh string/number sai.
- Cách dùng command dễ gây lỗi.

ShellCheck hỗ trợ phát hiện lỗi, không thay thế việc hiểu script và kiểm tra trên VM lab.

## Debug theo evidence

Khi script thất bại, ghi lại:

1. Input đã dùng.
2. Environment và working directory cần thiết.
3. Command cuối cùng chạy.
4. stdout/stderr.
5. Exit status.
6. File/state trước và sau.

## Test an toàn

Đầu tiên chạy trên dữ liệu giả trong thư mục lab. Nếu script có thao tác xóa/ghi, thêm chế độ dry-run hoặc in target trước khi thực hiện.

