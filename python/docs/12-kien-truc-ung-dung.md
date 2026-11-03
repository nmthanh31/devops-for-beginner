# Kiến trúc ứng dụng web và phân chia trách nhiệm

## 1. Tại sao không đặt mọi thứ trong một file?

Một file duy nhất hữu ích để học route đầu tiên. Khi thêm xác thực, parsing, cache, dịch vụ ngoài, metrics và config, một file lớn sẽ làm khó tìm lỗi, test và thay thế phụ thuộc.

Chia file không phải mục tiêu tự thân. Mỗi ranh giới nên giúp trả lời rõ: phần này nhận gì, làm gì, và phụ thuộc vào phần nào?

## 2. Các lớp trách nhiệm

```text
HTTP route/controller
    ↓
Application service
    ├── mapper/normalizer
    ├── dedup repository
    ├── ownership client
    └── notification service
             ↓
        external-service adapter
```

- **Route/controller:** HTTP method/path, schema, authentication, status code. Mỏng, không chứa toàn bộ logic.
- **Service/use case:** điều phối nghiệp vụ, ví dụ xử lý từng alert và quyết định gửi/bỏ qua.
- **Mapper/normalizer:** chuyển schema ngoài (API, file hoặc message queue) sang dạng nội bộ thống nhất.
- **Formatter:** biến dữ liệu nội bộ thành nội dung cần hiển thị/gửi; không tự gọi mạng.
- **Client/adapter:** giao tiếp với dịch vụ ngoài hoặc cache; che chi tiết giao thức bên ngoài.
- **Repository:** thao tác lưu/truy vấn dữ liệu nếu có database.

## 3. NestJS so với Python

NestJS có module, provider và dependency injection rõ ràng. Python/FastAPI không bắt buộc khung nặng tương tự. Có thể dùng package, module file và `APIRouter`; truyền service qua dependency hoặc khởi tạo ở composition root. Tổ chức vừa đủ giúp người mới đọc được luồng mà không dựng quá nhiều abstraction.

## 4. Composition root

Composition root là nơi tạo ứng dụng và nối dependency: settings, clients, services, routers. Trong NestJS nhiều phần do DI container đảm nhiệm. Với FastAPI, có thể dùng lifespan/app state/dependencies hoặc factory function. Tránh tạo kết nối Redis/HTTP cho mỗi request; client nên có vòng đời và đóng đúng cách.

## 5. Boundary và schema nội bộ

Payload từ một API ngoài là schema bên ngoài; không nên để mọi phần còn lại phụ thuộc trực tiếp vào format đó. Normalizer chuyển dữ liệu vào model nội bộ để service/formatter không phụ thuộc nhà cung cấp cụ thể.

Boundary rõ giúp:

- thay đổi API bên ngoài không lan toàn ứng dụng;
- kiểm tra mapper độc lập bằng fixture;
- xử lý thiếu label nhất quán;
- fake adapter trong unit test.

## 6. Lỗi theo từng lớp

- Lỗi request/schema: FastAPI trả 4xx.
- Alert không đủ dữ liệu: service quyết định bỏ qua, ghi metric hoặc trả lỗi phù hợp.
- Dịch vụ ngoài trả 429: adapter nhận biết giới hạn, cân nhắc retry có giới hạn.
- Redis lỗi: service cần chính sách rõ ràng; không lặng lẽ giả vờ dedup hoạt động.
- Bug không dự kiến: log có request ID, trả 500 không tiết lộ traceback/secret cho client.

Không dùng `except Exception: pass`; nó che mất lỗi và làm trạng thái hệ thống không thể tin cậy.

## 7. Một cấu trúc thư mục có thể phát triển dần

```text
app/
  main.py                 # tạo FastAPI app, mount routers
  api/routes/             # HTTP layer
  schemas/                # Pydantic request/response models
  services/               # nghiệp vụ
  integrations/            # external APIs, cache, message providers
  formatters/              # render nội dung
  core/                    # settings, logging, security
tests/
```

Không cần tạo hết thư mục ngay. Tạo file mới khi có trách nhiệm thật sự cần tách; dùng package `__init__.py` theo cách phù hợp với cách chạy/import dự án.

## 8. Dependency direction

Route có thể gọi service; service có thể gọi adapter interface/client. Formatter thuần thường không cần import FastAPI. Tránh để module formatting import route hoặc router import chi tiết database ở mọi nơi.

Quy tắc thực dụng: logic nghiệp vụ quan trọng nên có thể gọi từ test Python mà không phải dựng server HTTP.
