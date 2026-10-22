# Lab 02 — Quản lý thư viện cá nhân

## Đề bài

Hãy tự xây dựng một chương trình chạy trong terminal để quản lý bộ sưu tập sách cá nhân. Chương trình phải cho phép người dùng thêm, xem, tìm kiếm, cập nhật, xóa sách và xem thống kê. Dữ liệu phải được lưu bền vững giữa các lần chạy.

Bạn tự quyết định cách tổ chức chương trình, cấu trúc dữ liệu, tên hàm, cách chia module và cách kiểm thử. Không sử dụng thư viện bên ngoài.

## Thông tin mỗi cuốn sách

Mỗi cuốn sách cần có:

- mã sách duy nhất;
- tên sách;
- tác giả;
- năm xuất bản;
- trạng thái đọc: `Chưa đọc`, `Đang đọc` hoặc `Đã đọc`.

## Chức năng bắt buộc

Chương trình cần có menu cho phép người dùng:

1. Thêm sách mới.
2. Hiển thị toàn bộ sách, có đánh số thứ tự.
3. Tìm sách theo tên hoặc tác giả; không phân biệt chữ hoa/chữ thường.
4. Cập nhật thông tin hoặc trạng thái đọc của một cuốn sách.
5. Xóa sách sau khi xác nhận thao tác.
6. Xem thống kê: tổng số sách và số lượng theo từng trạng thái đọc.
7. Thoát chương trình.

## Quy tắc dữ liệu

- Mã sách không được trùng hoặc để trống.
- Tên sách và tác giả không được để trống.
- Năm xuất bản phải là số nguyên hợp lệ và không lớn hơn năm hiện tại.
- Trạng thái chỉ được nhận một trong ba giá trị đã nêu.
- Khi tìm kiếm không có kết quả, chương trình phải thông báo rõ.
- Khi thư viện chưa có sách, các chức năng xem và thống kê phải xử lý phù hợp.
- Dữ liệu phải được lưu vào file JSON. Mọi thao tác thêm, cập nhật hoặc xóa thành công phải được lưu ngay.
- Nếu file dữ liệu chưa tồn tại, chương trình bắt đầu với thư viện rỗng.
- Nếu file JSON bị hỏng hoặc không đúng cấu trúc, chương trình phải báo lỗi rõ ràng và không được âm thầm ghi đè làm mất dữ liệu.
- Nhập sai không được làm chương trình thoát đột ngột; người dùng cần có thể thử lại.

## Tiêu chí hoàn thành

- Chương trình chạy được từ đầu đến cuối mà không cần cài thư viện ngoài.
- Có thể thêm nhiều sách và các chức năng đọc/tìm/sửa/xóa hoạt động đúng.
- Dữ liệu vẫn chính xác sau khi thoát chương trình rồi chạy lại.
- Mã sách trùng, dữ liệu thiếu, năm sai và trạng thái không hợp lệ đều được xử lý.
- Có kiểm thử tự động cho các trường hợp chính, bao gồm dữ liệu hợp lệ và không hợp lệ.
- Không để thông tin của sách hoặc thao tác người dùng bị mất âm thầm khi xảy ra lỗi file.

## Bàn giao

Hoàn thành chương trình, file dữ liệu mẫu nếu cần, và các bài kiểm thử. Khi đã xong, gửi cấu trúc thư mục, cách chạy, kết quả test và những phần bạn thấy khó nhất để được review.
