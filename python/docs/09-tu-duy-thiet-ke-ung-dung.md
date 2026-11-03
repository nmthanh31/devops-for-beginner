# Tư duy thiết kế ứng dụng web và công cụ

Tài liệu này trình bày cách suy nghĩ trước khi viết code. Các khái niệm áp dụng cho nhiều loại ứng dụng, không gắn với một dự án cụ thể.

## 1. Bắt đầu từ bài toán, không bắt đầu từ thư viện

Trước khi chọn FastAPI, PostgreSQL hay Redis, hãy mô tả:

- Ai hoặc thành phần nào sử dụng ứng dụng?
- Dữ liệu nào đi vào?
- Ứng dụng phải làm gì với dữ liệu?
- Kết quả nào được trả ra hoặc tạo ra?
- Dữ liệu nào cần giữ sau khi chương trình dừng?
- Lỗi nào có thể xảy ra và người dùng cần biết gì?

Ví dụ một công cụ nhập dữ liệu: nhận file, kiểm tra dòng, lưu các bản ghi hợp lệ, báo dòng lỗi. Từ yêu cầu này mới suy ra cần đọc file, validation, database transaction và báo cáo kết quả.

## 2. Mô hình luồng dữ liệu

Vẽ một luồng trước khi chia file:

```text
nguồn dữ liệu → kiểm tra → chuẩn hóa → nghiệp vụ → lưu/gọi dịch vụ → kết quả
```

Luồng giúp tìm vị trí thích hợp cho từng trách nhiệm và phát hiện phần nào là tác dụng phụ như ghi DB, gửi HTTP hoặc tạo file.

## 3. Phân biệt dữ liệu ngoài và dữ liệu nội bộ

Dữ liệu từ HTTP, file hoặc môi trường là dữ liệu ngoài: có thể thiếu, sai kiểu, sai định dạng hoặc độc hại. Kiểm tra nó tại ranh giới ứng dụng.

Sau validation, chuyển sang cấu trúc nội bộ có ý nghĩa rõ ràng. Điều này tránh để các lớp xử lý nghiệp vụ phải kiểm tra lặp lại cùng một điều kiện ở mọi nơi.

## 4. Schema, validation và nghiệp vụ là ba việc khác nhau

- **Schema:** dữ liệu gồm trường nào và kiểu nào?
- **Validation:** dữ liệu có đáp ứng điều kiện hình thức không?
- **Business rule:** dữ liệu hợp lệ về hình thức có được phép trong tình huống này không?

Ví dụ chuỗi `"2030-01-01"` có thể hợp lệ về kiểu string, nhưng ngày đó có được đặt lịch hay không là quy tắc nghiệp vụ.

## 5. Tác dụng phụ

Hàm thuần tính toán đầu ra từ đầu vào mà không thay đổi bên ngoài; ví dụ chuẩn hóa tên hoặc tính tổng. Tác dụng phụ là gọi API, ghi file/database, gửi email hoặc sửa trạng thái.

Tách hàm thuần khỏi tác dụng phụ giúp test dễ hơn. Khi có lỗi, cũng dễ xác định đó là lỗi logic hay lỗi mạng/lưu trữ.

## 6. Nguồn sự thật và bản sao dữ liệu

Nếu một hệ thống là nguồn chuẩn, các hệ thống khác nên hiểu dữ liệu của mình là bản sao/cache chứ không được tự sửa rồi xem đó là sự thật. Cần xác định ai có quyền ghi, quy trình đồng bộ và cách xử lý khi nguồn chuẩn tạm thời không khả dụng.

## 7. Tính lặp lại an toàn

Chương trình thực tế thường chạy lại do retry, restart hoặc lịch định kỳ. Hãy hỏi: chạy lại cùng input có tạo bản ghi trùng, gửi thông báo trùng hoặc xóa dữ liệu không?

Idempotency, unique key, fingerprint và transaction là các cách giải quyết khác nhau cho những vấn đề khác nhau; không có một kỹ thuật duy nhất phù hợp mọi nơi.

## 8. Thiết kế lỗi và trạng thái giảm chất lượng

Không phải mọi dependency đều luôn sẵn sàng. Chọn trước hành vi khi database, API ngoài hoặc cache lỗi: dừng request, retry giới hạn, dùng cache cũ, tiếp tục với thông tin thiếu, hay đưa công việc vào queue.

Fallback phải minh bạch. Không tạo dữ liệu giả để làm response trông thành công.

## 9. Chọn mức kiến trúc phù hợp

Một script vài chục dòng có thể chỉ cần hàm và file cấu hình. Một web service có nhiều routes và dependency cần tách module. Chỉ thêm abstraction khi nó làm rõ trách nhiệm, giảm lặp hoặc giúp test/thay dependency; tránh tạo layer rỗng chỉ để trông giống kiến trúc lớn.

## 10. Câu hỏi review trước khi code

1. Input và output chính xác là gì?
2. Cái gì được xem là hợp lệ?
3. Nguồn dữ liệu chuẩn là đâu?
4. Thao tác nào có side effect?
5. Chuyện gì xảy ra khi chạy hai lần?
6. Dependency timeout hoặc trả lỗi thì sao?
7. Làm sao test logic mà không gọi dịch vụ thật?
