# Kiểm thử ứng dụng Python

## 1. Vì sao test?

Test là bằng chứng lặp lại được rằng hành vi mong đợi vẫn đúng sau khi sửa code. Một test tốt tập trung vào hành vi và kết quả, không kiểm tra chi tiết nội bộ không cần thiết.

## 2. Các tầng test

- **Unit:** hàm mapper, formatter, fingerprint thuần; nhanh và không cần mạng/DB.
- **Integration:** route + Pydantic, DB repository với test database, hoặc client adapter giả lập.
- **End-to-end:** gửi request qua app và xác nhận toàn luồng với các dependency được mock hoặc môi trường test.

Không nên gọi payment/email/cloud API thật trong test mặc định; tránh side effects, credential thật và flaky network.

## 3. pytest và assertion

pytest tìm các hàm `test_...`. `assert` so sánh kết quả mong đợi. Tách test thành trường hợp rõ: payload hợp lệ, field thiếu, namespace vắng, resolved event, special HTML characters.

## 4. FastAPI TestClient

TestClient cho phép gửi HTTP request vào ASGI app trong test mà không cần chạy Uvicorn riêng. Có thể kiểm tra status code, JSON body, validation errors và auth. Dependency override cho phép thay database, Redis hoặc auth thật bằng fake.

## 5. Fixtures và test data

Fixture là dữ liệu dùng lặp lại trong test. Lưu các JSON mẫu ở `tests/fixtures`; có thể tạo trường hợp đầy đủ, thiếu field, danh sách rỗng hoặc malformed payload. Fixture giúp test gần dữ liệu thực tế nhưng vẫn xác định được kết quả.

## 6. Mock và fake

Mock thay thế collaborator để test một đơn vị. Ví dụ mock email client và kiểm tra service gọi `send_message` đúng nội dung. Fake là implementation đơn giản có hành vi gần thật, như dictionary-backed cache.

Mock không chứng minh dịch vụ ngoài thật hoạt động; nó chứng minh code tương tác đúng contract. Cần thêm kiểm tra tích hợp riêng nếu muốn xác nhận configuration/network.

## 7. Test lỗi quan trọng

- 422 khi schema không hợp lệ.
- 401 khi credential sai.
- Dịch vụ ngoài trả rate limit, 5xx hoặc timeout.
- Dependency/cache không khả dụng hoặc tài nguyên không tìm thấy.
- Redis lỗi theo chính sách dedup đã chọn.
- Alert bị gửi lặp.
- Message escaping, thời gian và giới hạn độ dài.

## 8. Quy tắc thực tế

Test phải độc lập, không phụ thuộc thứ tự chạy, không dùng secret thật, dọn tài nguyên tạo ra. Khi test thất bại, đọc assertion/traceback trước; không sửa test để hợp thức hóa bug mà chưa hiểu yêu cầu.
