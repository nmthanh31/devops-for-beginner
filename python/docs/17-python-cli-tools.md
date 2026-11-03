# Viết công cụ dòng lệnh bằng Python

## 1. CLI là gì?

CLI (Command-Line Interface) là chương trình nhận lệnh/tham số từ terminal, thực hiện công việc rồi trả kết quả và exit code. Ví dụ tool nhập dữ liệu, kiểm tra cấu hình, xử lý file hoặc dọn cache.

CLI khác API server: CLI thường chạy một lần rồi thoát; API server ở trạng thái lắng nghe request liên tục.

## 2. `argparse`

`argparse` thuộc standard library, giúp định nghĩa lệnh, option, kiểu dữ liệu, help và validation cơ bản. Ví dụ một lệnh có thể nhận `--config`, `--dry-run` hoặc `sync-once`; không nên tự parse `sys.argv` thủ công khi command có nhiều option.

## 3. Exit code

Exit code `0` thường nghĩa là thành công; số khác 0 nghĩa là thất bại. Shell, CI/CD và scheduler dùng exit code để quyết định bước tiếp theo. In lỗi dễ hiểu ra stderr và trả mã thích hợp.

## 4. `pathlib` và filesystem

`pathlib.Path` biểu diễn đường dẫn độc lập hơn nối chuỗi bằng dấu `/` hoặc `\\`. Dùng `with` khi đọc/ghi file để tài nguyên được đóng. Kiểm tra quyền, file không tồn tại, encoding và file rỗng.

## 5. Chạy subprocess an toàn

Khi cần gọi `kubectl`, `helm` hoặc tool hệ thống, dùng subprocess với danh sách đối số thay vì ghép chuỗi shell từ input người dùng. Đặt timeout, kiểm tra return code và giới hạn output. Tránh `shell=True` trừ khi hiểu rõ rủi ro injection và có lý do cụ thể.

## 6. Idempotency và dry run

Tool vận hành có thể bị chạy lại. Thiết kế thao tác idempotent khi có thể. `--dry-run` hiển thị thay đổi dự kiến mà chưa áp dụng; hữu ích trước thao tác có tác động lớn. Log rõ resource và kết quả.

## 7. Logging và output

Output cho người dùng có thể ngắn, rõ; log kỹ thuật nên có level, timestamp, context. Không trộn progress messages với dữ liệu machine-readable JSON nếu tool cần pipe output sang chương trình khác.

## 8. Cấu hình và secret

Nhận cấu hình từ file hoặc environment; không hardcode token. Khi tool chạy trong CI, secrets dùng cơ chế secret store của CI và không bật shell trace làm lộ biến.
