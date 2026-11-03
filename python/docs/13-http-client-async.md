# Gọi dịch vụ HTTP, httpx và async

## 1. Một ứng dụng có thể vừa là server vừa là client

Ứng dụng có thể nhận HTTP request ở một route, rồi gọi API khác để lấy dữ liệu hoặc thực hiện tác vụ. FastAPI chủ yếu xử lý chiều vào; `httpx` là một HTTP client dùng cho chiều ra.

```text
Client A ──request──► Web service ──request──► External API
Client A ◄─response── Web service ◄─response── External API
```

## 2. Vì sao dùng httpx?

HTTP client thư viện quản lý kết nối, headers, body JSON, timeout và response. `httpx` hỗ trợ cả API đồng bộ và bất đồng bộ. Không nên tự nối socket HTTP hoặc tự parse protocol.

## 3. Timeout là bắt buộc

Nếu không đặt timeout, một upstream treo có thể giữ request, worker hoặc connection lâu không giới hạn. Đặt connect/read/write/pool timeout theo tính chất nghiệp vụ. Timeout là lỗi tạm thời có thể retry, nhưng retry phải giới hạn.

## 4. Retry và backoff

Retry có ích cho lỗi mạng, 429 hoặc một số 5xx. Backoff tăng khoảng chờ theo lần thử để không dồn request vào dịch vụ đang lỗi. Có thể thêm jitter để nhiều instance không retry cùng nhịp.

Không retry mù:

- 401/403 thường cần sửa credential/quyền, retry không giải quyết.
- Một POST có thể đã thành công dù client timeout trước khi nhận response; retry có thể lặp tác dụng phụ.
- Retry vô hạn làm cạn tài nguyên.

Phân biệt lỗi kết nối, timeout, status HTTP và lỗi parse response. Log mã/status/request ID nhưng không log token.

## 5. Connection pooling và vòng đời client

HTTP client giữ kết nối tái sử dụng, giảm handshake và tài nguyên. Tạo một client cho app/service lifetime, không tạo mới cho mỗi request nếu có thể. Khi app shutdown, đóng client để giải phóng socket.

## 6. Đồng bộ và bất đồng bộ

I/O-bound là công việc chủ yếu chờ mạng hoặc disk. `async` cho phép một event loop chuyển sang request khác trong lúc chờ I/O, nhưng cần dùng async client và `await` xuyên suốt.

```text
async endpoint + await async_http_client → event loop có thể phục vụ việc khác
async endpoint + gọi HTTP đồng bộ chặn → event loop bị block
```

`async` không tự làm CPU-heavy computation nhanh hơn. Với xử lý CPU nặng cần process/thread hoặc worker riêng.

## 7. Tác dụng phụ khi gọi upstream

Gửi email, thanh toán, tạo bản ghi hoặc phát hành lệnh là side effect. Cần nghĩ về timeout sau khi upstream đã xử lý, khả năng gửi lặp, idempotency key, rate limit và lưu dấu kết quả. Gọi API chỉ đọc thường dễ retry hơn thao tác tạo/sửa dữ liệu.

## 8. Xử lý response

HTTP 4xx/5xx không phải lúc nào cũng tự biến thành exception trong mọi client. Kiểm tra status theo API, parse JSON có kiểm soát, xác thực response schema và đưa lỗi ra service dưới dạng có ý nghĩa. Không trả nguyên response nhạy cảm của upstream về caller.
