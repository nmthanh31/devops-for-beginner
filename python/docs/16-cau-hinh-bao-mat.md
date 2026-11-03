# Cấu hình, bảo mật và quản lý lỗi

## 1. Cấu hình khác code

Code mô tả hành vi; cấu hình thay đổi theo môi trường: port, log level, external API URL, timeout. Environment variables giúp cùng một image chạy local/test/production với cấu hình khác nhau.

`.env.example` chỉ chứa tên biến và giá trị giả. File `.env` thật phải nằm trong `.gitignore`; secret production nên lấy từ secret manager/Kubernetes Secret.

## 2. Secret và xác thực

API token, webhook password và database credential không được hardcode, commit, in log hay trả về trong error response. Hạn chế quyền credential, hỗ trợ rotation và chỉ cấp secret cần thiết cho từng service.

Webhook auth xác định caller có credential hợp lệ không. Authentication khác authorization: biết caller là ai không đồng nghĩa caller được phép làm mọi thứ.

Basic Auth chỉ an toàn khi dùng HTTPS trên mạng không tin cậy. So sánh password/token cẩn thận, không đưa chúng vào query string.

## 3. Input validation và trust boundary

Mọi dữ liệu ngoài đều chưa đáng tin: HTTP request, response từ API, environment variables, file JSON. Pydantic kiểm tra cấu trúc; nghiệp vụ cần kiểm tra điều kiện domain. Escape nội dung trước khi đưa dữ liệu không tin cậy vào HTML/Markdown hoặc giao diện khác để tránh làm hỏng format hay tạo nội dung nguy hiểm.

Validation không thay thế authentication; authentication không thay thế validation.

## 4. Lỗi và exception

Exception dùng để báo tình huống bất thường. Bắt lỗi ở nơi có thể xử lý hoặc bổ sung ngữ cảnh; nếu không thể phục hồi, để lỗi lan tới handler/log phù hợp. Không bắt tất cả rồi trả `success: true`.

Tách lỗi do input, dependency tạm thời, credential/quyền, và bug nội bộ. API response nên đủ hữu ích nhưng không lộ traceback, token, host nội bộ hay dữ liệu nhạy cảm.

## 5. Logging

Log là bản ghi sự kiện vận hành. Dùng level phù hợp (`DEBUG`, `INFO`, `WARNING`, `ERROR`), có request ID/sync ID để nối sự kiện, không ghi toàn bộ payload nếu có dữ liệu nhạy cảm. Log mỗi lỗi một lần ở tầng phù hợp để tránh trùng lặp.

## 6. Retry, rate limit và timeout

Retry chỉ cho lỗi có khả năng tạm thời, có giới hạn và backoff. Thêm timeout cho mọi I/O. Xử lý HTTP 429 theo `Retry-After` nếu có; tránh tạo vòng retry gây quá tải.

## 7. Least privilege và mạng

Credential kết nối nguồn dữ liệu chỉ nên có quyền tối thiểu. API chỉ expose chức năng cần thiết. Database/cache không public nếu không cần. Trong Kubernetes dùng service account/quyền tối thiểu, NetworkPolicy nếu khả dụng, non-root container và TLS trên mạng không tin cậy.
