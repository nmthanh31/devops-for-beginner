# Docker, health check, logging và metrics

## 1. Container và image

Image là gói bất biến chứa runtime, dependencies và code; container là tiến trình đang chạy từ image. Image không nên chứa secret thật. Tạo image nhỏ, chạy non-root và pin dependency có kiểm soát.

## 2. Docker Compose

Compose mô tả nhiều service local: gateway, Redis, PostgreSQL hoặc mock upstream. Service có thể gọi nhau bằng DNS service name; volume giữ dữ liệu PostgreSQL qua vòng đời container. `depends_on` không luôn đồng nghĩa dependency đã sẵn sàng nhận kết nối; healthcheck/retry vẫn cần.

## 3. Environment và filesystem container

Container có filesystem riêng. Không mặc định rằng file trên host xuất hiện trong container; cần mount volume nếu muốn. Cấu hình truyền qua environment/secret. Không bake `.env` production vào image.

## 4. Liveness và readiness

- **Liveness:** tiến trình còn sống hay bị treo cần restart?
- **Readiness:** service hiện có thể nhận traffic chưa, dependencies cần thiết đã sẵn sàng chưa?

Health endpoint đơn giản chỉ chứng minh app trả lời HTTP, không nhất thiết chứng minh database hoặc mọi dịch vụ ngoài hoạt động. Thiết kế check không làm probe tự gây tải hoặc phụ thuộc không cần thiết.

## 5. Metrics và logs

Logs mô tả sự kiện cụ thể; metrics đo số liệu tổng hợp theo thời gian. Ví dụ: request count, validation failures, upstream errors, duplicate jobs, processing latency.

Tránh label có cardinality cao như namespace, pod, user ID hoặc fingerprint cho mỗi event; số series sẽ bùng nổ. Không đưa secret/PII vào log hoặc metric labels.

## 6. Graceful shutdown

Kubernetes gửi SIGTERM trước khi dừng container. Ứng dụng nên ngừng nhận công việc mới, hoàn thành/đóng những gì có thể, đóng HTTP/DB clients và thoát trong thời gian grace period. Không giả định process luôn có thể chạy đến hết công việc khi bị kill.

## 7. Kubernetes deployment

Deployment mô tả số replica, image, env, resources và probes. Service cung cấp địa chỉ mạng ổn định. ConfigMap dành cho cấu hình không bí mật; Secret cho credential nhưng cần RBAC và secret management phù hợp. Requests/limits giúp scheduler và kernel quản lý tài nguyên.

Local Compose test cách đóng gói cơ bản; nó không chứng minh đã tương thích production Kubernetes. Cần kiểm tra quyền, network, TLS, probe, resource limits và rollout thực tế.
