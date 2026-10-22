# Bài 4 — Input validation và file safety

## Không tin input mặc định

Input có thể đến từ argument, environment, file, command substitution hoặc output của command khác. Trước khi dùng input trong path hoặc command, cần kiểm tra nó có đúng loại và phạm vi không.

Các câu hỏi cơ bản:

- Có rỗng không?
- Có phải path tuyệt đối/đúng thư mục lab không?
- Có chứa `..`, newline hoặc ký tự ngoài dự kiến không?
- Target có phải file regular không?
- Có đang là symlink không?
- Có chắc đây là resource của lab không?

## Kiểm tra trước khi xóa hoặc ghi

Các thao tác `rm`, `mv`, `cp`, `chmod`, `chown`, `mkfs` và redirect `>` có thể làm thay đổi dữ liệu. Script nên kiểm tra target trước và giới hạn phạm vi thao tác.

Không dùng `rm -rf` trên path được tạo từ biến nếu chưa xác nhận biến không rỗng và trỏ đúng thư mục lab.

## Temporary file

File tạm cần có tên khó đoán và quyền phù hợp. Tránh tự ghép tên trong `/tmp` theo cách có thể bị process khác tạo trước hoặc thay thế.

## `find` và action

`find` có thể lọc theo type, size, age rồi thực hiện action. Cần test phần điều kiện trước khi thêm action xóa hoặc thay đổi quyền.

Tư duy an toàn:

```text
find ... -print       # xem target
find ... -print0      # xác nhận target có khoảng trắng
find ... -delete      # chỉ chạy sau khi kiểm tra phạm vi
```

## Nguồn

- [LPIC-1 103.3/105.2 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

