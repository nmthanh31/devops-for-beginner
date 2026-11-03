# Nền tảng Web, HTTP và API

## 1. Client, server và request/response

Client là thành phần yêu cầu dữ liệu hoặc gửi công việc: trình duyệt, `curl`, ứng dụng desktop hay một service khác. Server lắng nghe kết nối, nhận request, chạy logic phù hợp rồi trả response.

```text
Client ── HTTP request ──► Server
Client ◄─ HTTP response ── Server
```

Một ứng dụng có thể vừa là server vừa là client. Ví dụ một web service nhận request từ trình duyệt rồi gọi API của nhà cung cấp khác.

## 2. URL và endpoint

URL có thể gồm scheme, host, port, path và query:

```text
http://127.0.0.1:8000/api/v1/items?category=book&page=2
```

- `http`: giao thức.
- `127.0.0.1`: máy hiện tại; từ container khác, địa chỉ này thường không trỏ tới host bạn mong muốn.
- `8000`: cổng server.
- `/api/v1/items`: path.
- Sau `?`: query parameters.

Endpoint thường được xác định bởi cặp **HTTP method + path**. `GET /items` khác `POST /items`; `/item` khác `/items`.

## 3. Cấu tạo HTTP request

Request có method, URL, headers và có thể có body. Header là metadata. Ví dụ `Content-Type: application/json` nói body là JSON. `Authorization` có thể mang thông tin xác thực.

```http
POST /api/v1/events HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{"type":"report-ready","source":"scheduler"}
```

Không phải request nào cũng có body; GET thường dùng query parameters cho bộ lọc/tìm kiếm. Không đưa token vào URL vì URL dễ bị lưu trong log và lịch sử.

## 4. GET và POST

**GET** dùng để đọc hoặc truy vấn dữ liệu. Theo quy ước, GET không nên tạo tác dụng phụ. GET có thể được cache, bookmark hoặc gọi tự động nên không dùng nó để gửi email, xóa dữ liệu hay thay đổi cấu hình.

**POST** gửi dữ liệu để server tiếp nhận hoặc xử lý. POST không đồng nghĩa luôn là “tạo một bản ghi”; nó cũng dùng cho form, webhook, command và một số truy vấn phức tạp.

Method không tự bảo vệ dữ liệu. Body của POST vẫn cần HTTPS để được mã hóa khi đi qua mạng.

## 5. Response và status code

Response chứa status code, headers và thường có body. Các mã thường gặp:

- `200 OK`: xử lý thành công, có kết quả.
- `201 Created`: tạo tài nguyên thành công.
- `202 Accepted`: đã nhận công việc, thường dùng khi xử lý tiếp sau đó; không nên tuyên bố “đã hoàn tất” nếu chỉ mới nhận.
- `204 No Content`: thành công nhưng không có body.
- `400 Bad Request`: request sai ở mức nghiệp vụ/định dạng.
- `401 Unauthorized`: thiếu hoặc sai xác thực.
- `403 Forbidden`: đã xác thực nhưng không đủ quyền.
- `404 Not Found`: không có route/tài nguyên phù hợp.
- `409 Conflict`: xung đột, ví dụ trùng khóa.
- `422 Unprocessable Content`: request khớp route nhưng dữ liệu không qua validation.
- `429 Too Many Requests`: bị giới hạn tốc độ.
- `500`/`502`/`503`: lỗi server hoặc upstream.

Chọn mã phản hồi nhất quán giúp client quyết định retry, báo lỗi hay dừng.

## 6. JSON và API contract

JSON là định dạng trao đổi dữ liệu dạng object, array, string, number, boolean và null. API contract là thỏa thuận về method, path, headers, schema request, schema response và lỗi.

Pydantic model là một cách thể hiện contract trong FastAPI. Swagger/OpenAPI có thể sinh tài liệu từ các routes và models này. Khi đổi field hoặc ý nghĩa status code, có thể cần cập nhật client và tests.

## 7. Statelessness, idempotency và retry

HTTP API thường được thiết kế stateless: mỗi request mang đủ thông tin xác thực/ngữ cảnh cần thiết; server không dựa vào trạng thái ngầm trong trình duyệt. Dữ liệu nghiệp vụ vẫn có thể lưu trong database/cache.

Idempotent nghĩa là gửi cùng thao tác nhiều lần có kết quả cuối tương đương với gửi một lần. GET thường idempotent. POST có thể không idempotent nếu mỗi lần gửi tạo hóa đơn hoặc gửi thông báo mới. Vì mạng có thể timeout sau khi server đã xử lý, client có thể retry; hệ thống cần idempotency key hoặc cơ chế nhận diện bản lặp khi tác dụng phụ không được lặp.

## 8. Swagger UI

`/docs` là giao diện tài liệu tương tác được sinh từ OpenAPI. Nó giúp đọc endpoints và schemas, rồi gửi request thử. Đây không phải giao diện nghiệp vụ cho người dùng cuối.

## 9. localhost và mạng container

`127.0.0.1` luôn có nghĩa “chính môi trường đang gọi”. Trong container, nó chỉ container đó, không tự trỏ đến máy host hoặc container khác. Docker Compose thường cho các service gọi nhau bằng DNS service name.
