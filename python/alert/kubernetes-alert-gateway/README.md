# KOS — Kubernetes Alert Gateway bằng Python

README này hướng dẫn bạn tự xây phiên bản Python của dự án NestJS `kubernetes-alert-gateway`. Trong workspace này, **KOS là tên của Kubernetes Alert Gateway Python**. Tài liệu lý thuyết tổng quát nằm trong [`../../docs/README.md`](../../docs/README.md); tài liệu này chỉ hướng dẫn ứng dụng cụ thể.

## 1. Mục tiêu

KOS nhận webhook từ Falco và Prometheus Alertmanager, xác thực caller, kiểm tra payload, chuẩn hóa alert, chống xử lý trùng, bổ sung ownership context nếu cấu hình, định dạng nội dung rồi gửi Telegram.

```text
Falco / Alertmanager
        │ HTTP POST + JSON
        ▼
FastAPI routes → Pydantic schemas → application services
                                      ├─ normalize/map
                                      ├─ dedup (Redis)
                                      ├─ ownership lookup (Rancher hoặc service metadata)
                                      └─ formatter → Telegram client
```

Không cần chuyển từng dòng TypeScript sang Python. Bảo toàn hành vi và contract cần thiết, nhưng dùng cách tổ chức Python dễ đọc và dễ test.

## 2. Đối chiếu NestJS với Python

| NestJS | Trách nhiệm | Python thường dùng |
|---|---|---|
| Controller | Nhận HTTP request | FastAPI route / `APIRouter` |
| DTO + `class-validator` | Schema và validation | Pydantic `BaseModel` |
| Injectable service | Nghiệp vụ | Hàm hoặc class service |
| Mapper | Chuẩn hóa payload ngoài | Hàm thuần + model nội bộ |
| Axios | Gọi API ngoài | `httpx` |
| ioredis | Cache/dedup | Redis client Python |
| Jest | Test | `pytest` |
| ConfigService | Cấu hình | Environment variables / settings |

Đây là đối chiếu về vai trò, không phải ánh xạ một-một. Python không bắt buộc tạo class/module cho mọi thứ.

## 3. Class, `BaseModel` và payload lồng nhau

### Class và object

Class mô tả cấu trúc; object/instance là một giá trị cụ thể theo cấu trúc đó. `AlertItem` mô tả một alert; một instance của nó tương ứng một alert cụ thể.

### Vì sao kế thừa `BaseModel`?

`BaseModel` của Pydantic biến type hints thành schema có thể kiểm tra lúc chạy. FastAPI nhận JSON, Pydantic xác thực rồi chuyển thành object Python. Nếu field bắt buộc thiếu hoặc sai kiểu, route không chạy và FastAPI thường trả `422`.

### Vì sao tách `AlertItem` và payload ngoài?

Payload Alertmanager có một object bao ngoài; trường `alerts` là danh sách, mỗi phần tử lại là một object alert. Mỗi class mô tả đúng một tầng:

```json
{
  "status": "firing",
  "receiver": "telegram-webhook",
  "alerts": [
    {
      "status": "firing",
      "labels": {"alertname": "KubePodCrashLooping", "namespace": "production"},
      "annotations": {"summary": "Pod is restarting frequently"}
    }
  ]
}
```

```python
from typing import Literal
from pydantic import BaseModel

class AlertItem(BaseModel):
    status: Literal["firing", "resolved"]
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None

class AlertmanagerPayload(BaseModel):
    status: Literal["firing", "resolved"]
    receiver: str
    alerts: list[AlertItem]
```

- `Literal[...]` giới hạn giá trị được phép.
- `dict[str, str]` là dictionary có key/value kiểu chuỗi.
- `| None = None` cho phép field vắng mặt.
- `list[AlertItem]` là danh sách các object theo schema `AlertItem`.

Đây là schema tối thiểu để học. Chỉ thêm các field khác sau khi xác định ứng dụng cần dùng và kiểm tra với payload fixture.

## 4. HTTP method, body và response

Endpoint được xác định bởi **method + path**. GET thường để đọc; POST thường gửi dữ liệu để xử lý. Alertmanager gửi POST vì payload nằm trong JSON body.

```python
@app.post("/api/v1/webhooks/alertmanager", status_code=202)
def receive_alert(payload: AlertmanagerPayload):
    ...
```

`payload: AlertmanagerPayload` yêu cầu FastAPI đọc body và xác thực model. Mã `202` nghĩa là đã chấp nhận request; chỉ chọn nếu semantics của quá trình xử lý phù hợp. `404` thường do method/path không khớp; `422` thường do body không qua validation.

## 5. Trạng thái code hiện tại

`app.py` bắt đầu bằng các bài tập nhỏ: health endpoint, GET query, model Pydantic và POST. Trước khi tiến xa hơn, tự rà soát:

- Route POST đã nhận `AlertmanagerPayload` hay còn nhận `TestAlert`?
- Response có field placeholder hoặc lỗi chính tả không?
- Ownership route có thuộc scope gateway hay chỉ là bài thực hành riêng?
- Uvicorn có đang chạy từ đúng thư mục chứa `app.py` không?

## 6. Chuẩn bị môi trường local

Trong Git Bash, từ thư mục gốc repo:

```bash
cd /d/Documents/F/python/alert/kubernetes-alert-gateway
python --version
python -m venv .venv
source .venv/Scripts/activate
python -c "import sys; print(sys.executable)"
python -m pip install fastapi uvicorn httpx pydantic pytest
```

Không copy `.venv` từ thư mục khác: activation script lưu đường dẫn môi trường. Khi dependency ổn định, khai báo lại trong `requirements.txt` hoặc `pyproject.toml`.

Chạy app:

```bash
python -m uvicorn app:app --reload
```

`app:app` nghĩa là module `app.py` và biến FastAPI tên `app`. `/docs` hiển thị API docs; `/health` kiểm tra app.

## 7. Lộ trình tự triển khai từ đầu đến cuối

Mỗi phase gồm một khái niệm, một phần code bạn tự viết và tiêu chí kiểm tra. Chưa sang phase sau cho đến khi giải thích được phase hiện tại.

### Phase A — HTTP và API nền tảng

Học client/server, method/path, query/body, JSON, response codes, FastAPI route.

Làm health route, GET tra cứu thử, POST JSON. Hoàn thành khi biết giải thích `200`, `202`, `404`, `422` và kiểm tra được request qua `curl`/`/docs`.

### Phase B — Payload Alertmanager thật

Học class, Pydantic, nested model, `Literal`, `list`, `dict`, optional fields.

Thay model tập luyện bằng model phù hợp fixture Alertmanager của dự án NestJS. Test firing, resolved, nhiều alerts, thiếu field và status không hợp lệ.

### Phase C — Tách route và service

Học module/package, separation of concerns và dependency direction.

Route chỉ xác thực HTTP, nhận model, gọi service và trả response. Service điều phối nghiệp vụ. Bắt đầu tách `api/routes`, `schemas` và `services` khi code đã có trách nhiệm khác nhau.

### Phase D — Chuẩn hóa và format

Học mapping, dữ liệu ngoài/nội bộ, hàm thuần, escaping.

Map payload thành model nội bộ; lấy alert name, severity, cluster, namespace, workload, summary. Formatter dựng tin nhắn, xử lý field thiếu, HTML/Markdown escaping, message limit. Viết unit test cho từng tình huống.

### Phase E — Telegram client

Học HTTP client, timeout, status, exception, retry/backoff.

Dùng `httpx` với timeout và client có vòng đời; token lấy từ environment; xử lý 401/403/429/5xx; mock Telegram trong tests. Không retry vô hạn hoặc lộ token.

### Phase F — Authentication, dedup, ownership

Học authentication/authorization, secret management, Redis TTL, idempotency, fallback.

Bảo vệ webhook; xác định fingerprint và TTL; tái tạo ownership enrichment từ gateway NestJS. Chọn rõ Rancher API trực tiếp hay metadata service riêng. Khi dependency lỗi/không tìm thấy, không tự tạo Owner giả.

### Phase G — Kiểm thử và vận hành

Học pytest, mocks/fixtures, structured logging, health/readiness, metrics, Docker/Kubernetes.

Chạy tests offline; không cần Telegram/Rancher thật. Image không chứa secret; container non-root; probes/resources đúng; metrics tránh labels cardinality cao; có hướng dẫn deploy/troubleshooting.

## 8. Thử request khi model đã được nối vào POST

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/webhooks/alertmanager \
  -H "Content-Type: application/json" \
  -d '{"status":"firing","receiver":"test","alerts":[{"status":"firing","labels":{"alertname":"HighCPU","severity":"warning"},"annotations":{"summary":"CPU cao"}}]}'
```

`-i` hiển thị response headers/status; `-H` khai báo content type; `-d` gửi JSON body. Request được chấp nhận mới chứng minh route/schema hoạt động, chưa chứng minh Telegram đã gửi thành công.

## 9. Bảo mật và độ tin cậy

- Không commit `.env`, Telegram token, webhook password hoặc Rancher credential.
- Đặt timeout cho mọi mạng; retry có giới hạn.
- Không log secret hoặc payload nhạy cảm.
- POST có thể tạo side effect; cần dedup khi caller retry.
- Không coi timeout khi đọc nguồn dữ liệu là bằng chứng resource đã bị xóa.
- Không dùng `except Exception: pass`.
- Không tuyên bố đã kiểm chứng production nếu mới chạy local/mock.

## 10. Cách học với README này

Đọc một phase, tự viết, chạy test/lệnh kiểm tra, ghi lại lỗi và gửi phần code/error để review. Mỗi lần chỉ thêm một khái niệm mới. README giải thích mục tiêu và lý do; phần code chính bạn tự viết để học được thực chất.
