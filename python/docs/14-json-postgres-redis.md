# JSON, PostgreSQL, Redis và tính nhất quán dữ liệu

## 1. JSON không phải database

JSON là định dạng trao đổi/serialization. Có thể lưu cấu hình hoặc fixture JSON vào file, nhưng file JSON không tự cung cấp transaction, truy vấn đồng thời, index hay locking như database.

Request/response API thường dùng JSON; Pydantic parse JSON thành object đã kiểm tra. Fixture JSON giúp test xử lý dữ liệu với ví dụ lặp lại được.

## 2. PostgreSQL: dữ liệu bền vững có cấu trúc

Database quan hệ lưu dữ liệu trong bảng, hàng và cột. Foreign key mô tả quan hệ và bảo đảm tham chiếu hợp lệ; unique constraint ngăn bản ghi trùng; index giúp truy vấn nhanh nhưng có chi phí ghi/lưu trữ.

PostgreSQL phù hợp với dữ liệu quan hệ cần truy vấn, constraint và giữ lịch sử, như khách hàng/đơn hàng hoặc tài sản/nhóm. Không phải ứng dụng nào cũng cần database; chọn theo yêu cầu lưu trữ và truy vấn.

## 3. Transaction và commit

Transaction gộp nhiều thao tác DB thành một đơn vị: commit nếu tất cả thành công, rollback nếu lỗi. Ví dụ cập nhật project và namespace liên quan cần tránh trạng thái nửa cũ nửa mới.

Transaction database không bao gồm thao tác với dịch vụ ngoài. Không giữ DB transaction mở trong lúc chờ mạng lâu; thường commit dữ liệu cần thiết trước/sau theo thiết kế.

## 4. Upsert, reconciliation và soft delete

Upsert tạo bản ghi nếu chưa có hoặc cập nhật nếu đã có, dựa trên unique key. Idempotent sync có nghĩa chạy lại cùng dữ liệu không tạo duplicate.

Reconciliation so sánh snapshot mới với dữ liệu đã lưu. Chỉ đánh dấu resource đã mất sau lần đồng bộ đầy đủ thành công; nếu nguồn dữ liệu timeout thì không được diễn giải “không fetch được” thành “mọi resource đã bị xóa”. Soft delete/archived giữ lại dấu vết lịch sử.

## 5. Redis: cache hoặc state ngắn hạn

Redis là kho key-value trong bộ nhớ, hữu ích cho TTL cache, dedup fingerprint, rate limit và lock ngắn hạn. Nó khác PostgreSQL: không mặc định là nguồn dữ liệu lịch sử bền vững cho ownership metadata.

Dedup key có thể gồm fingerprint alert; TTL giúp cùng một alert không gửi lặp vô hạn. Quyết định TTL dựa trên vòng đời alert và hành vi resolved/update.

## 6. Idempotency và tác dụng phụ

Client có thể gửi lại event khi timeout. Service cần xác định khóa idempotency ổn định và quyết định request nào là bản lặp. Không chỉ băm toàn bộ JSON nếu trường thời gian/field không ổn định làm khóa thay đổi.

Nếu Redis không khả dụng, chọn chính sách:

- fail closed: không gửi vì không thể bảo đảm dedup;
- fail open: tiếp tục gửi, chấp nhận duplicate;
- queue/degraded mode.

Phải ghi rõ lựa chọn và metric/log quan sát được.

## 7. Migrations

Schema database thay đổi theo thời gian. Migration ghi lại từng bước thay đổi để các môi trường phát triển/test/production có thể nâng cấp nhất quán. Không sửa schema production thủ công rồi bỏ quên migration.
