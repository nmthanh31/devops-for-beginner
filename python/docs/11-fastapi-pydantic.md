# FastAPI và Pydantic

## 1. Framework là gì?

Framework cung cấp cấu trúc và quy ước để xây ứng dụng. FastAPI nhận HTTP request, tìm route phù hợp, chuyển dữ liệu vào hàm Python, gọi validation và biến kết quả thành HTTP response. Uvicorn là ASGI server chạy ứng dụng; FastAPI và Uvicorn là hai thành phần khác nhau.

```text
curl/client → Uvicorn → FastAPI route → hàm Python → response
```

## 2. Route và decorator

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

Decorator `@app.get(...)` gọi cơ chế đăng ký route của ứng dụng. Hàm `health` được gọi khi request method/path khớp. Tên hàm không quyết định URL; decorator mới quyết định path.

Khi route nhiều, `APIRouter` cho phép nhóm endpoints theo miền chức năng, ví dụ tài khoản, sản phẩm hoặc health. Router giúp chia file, nhưng vẫn cần service riêng cho nghiệp vụ.

## 3. Dữ liệu đến từ đâu?

- Tham số đường dẫn: `/clusters/{cluster_id}`.
- Query: `?namespace=tand`; phù hợp bộ lọc/tra cứu.
- Header: xác thực, request ID, content type.
- Body: JSON gửi trong POST/PUT/PATCH; thường mô tả bằng Pydantic model.

FastAPI suy luận nguồn dữ liệu từ cách khai báo tham số, nhưng nên dùng `Path`, `Query`, `Header`, `Body` rõ ràng khi cần validation hoặc mô tả tốt hơn.

## 4. Python class, instance và model

Class là định nghĩa cấu trúc; instance là một giá trị cụ thể được tạo theo định nghĩa. `AlertItem` là loại dữ liệu; một alert cụ thể là instance `AlertItem`.

`BaseModel` là class nền của Pydantic. Kế thừa nó biến type hints và field defaults thành schema mà Pydantic có thể parse và validate. Mục đích chính ở biên HTTP là biến dữ liệu JSON chưa tin cậy thành object có cấu trúc rõ ràng.

Không nhầm `BaseModel` với class Python thông thường: class thường không tự kiểm tra dữ liệu. Pydantic model có validation/serialization, schema generation và tích hợp FastAPI.

## 5. Các kiểu dữ liệu thường gặp trong schema

- `str`, `int`, `bool`: kiểu cơ bản.
- `list[AlertItem]`: mảng các object AlertItem.
- `dict[str, str]`: object JSON có key/value dạng chuỗi.
- `str | None`: giá trị chuỗi hoặc null.
- `field: str | None = None`: trường không bắt buộc; giá trị mặc định là None.
- `Literal["firing", "resolved"]`: tập giá trị cho phép giới hạn.

`str` chỉ kiểm tra đó là chuỗi, không tự giới hạn nội dung. Với `Literal`, Pydantic từ chối giá trị khác. Dùng `Field` khi cần min/max length, numeric bounds, alias hay default factory.

## 6. Nested models

```python
class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderPayload(BaseModel):
    customer_id: int
    items: list[OrderItem]
```

JSON lồng object/list thì schema cũng lồng model/list. Đây giúp lỗi được chỉ rõ tới vị trí như `body.items.0.quantity`; đồng thời IDE và OpenAPI hiểu được cấu trúc.

## 7. Validation và lỗi 422

Khi request tới route có tham số Pydantic, FastAPI đọc body, Pydantic kiểm tra required fields/types/constraints. Nếu sai, FastAPI tạo phản hồi 422 có danh sách lỗi. Hàm route không chạy, tránh để nghiệp vụ xử lý dữ liệu sai.

Validation không thay thế nghiệp vụ. Model có thể kiểm tra `namespace` là chuỗi không rỗng; service vẫn cần quyết định namespace đó có tồn tại trong dữ liệu đồng bộ hay user có quyền hay không.

## 8. Request model và response model

Request model mô tả dữ liệu client được phép gửi. Response model mô tả dữ liệu API cam kết trả ra. Tách hai model giúp không vô tình trả về token, email nội bộ hoặc cột database không nên công khai.

Có thể khai báo `response_model=...` trên route để FastAPI kiểm tra/serialize response và sinh OpenAPI. Không trả trực tiếp ORM model tùy tiện khi chưa kiểm soát schema.

## 9. Dependency injection

Dependency là thành phần route cần dùng nhưng không nên tự tạo rải rác bên trong route: database session, settings, auth principal, service. FastAPI `Depends` cung cấp các thành phần này theo cách có thể thay thế trong tests.

Dependency injection giúp test thay DB thật bằng fake session hoặc thay xác thực thật bằng fixture. Không cần lạm dụng cho một hàm thuần nhỏ.

## 10. Sync và async endpoint

`def` phù hợp code đồng bộ; `async def` phù hợp khi các thao tác I/O bên trong có API async và có `await`. Không thêm `async` chỉ vì ứng dụng là web. Gọi thư viện blocking như `requests` hoặc đồng bộ DB trực tiếp trong async route có thể chặn event loop.

## 11. Tài liệu OpenAPI

FastAPI dùng route, annotations và Pydantic models để tạo OpenAPI. `/docs` hiển thị method, parameters, schemas và cho phép gửi thử request. Nếu model sơ sài, tài liệu cũng sơ sài; schema tốt có giá trị cho người viết lẫn người dùng API.
