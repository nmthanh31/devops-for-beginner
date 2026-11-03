# N08 Bài 2 — Reverse proxy, load balancer và backend

> **Sau bài này bạn sẽ:**
> - Hiểu một request qua proxy gồm **nhiều TCP connection độc lập**.
> - Đọc được khối cấu hình chính của **Nginx** và **HAProxy**.
> - Biết health check, ACL, timeout ảnh hưởng tới 502/503/504 thế nào.
>
> **Cần trước:** [Bài 1](./01-http-tls.md).

---

## 1. Reverse proxy là gì

Proxy **đứng thay backend**: nhận request, có thể terminate TLS, chọn upstream, ghi log, trả response. Client chỉ biết proxy; proxy biết backend IP:port và health.

```text
client ──TCP#1/TLS──► Nginx:443 ──TCP#2──► HAProxy:8080 ──TCP#3──► app A :8081
                                                       └─TCP#3'─► app B :8082
```

Hệ quả:

- **Mỗi cạnh là một connection riêng** → test từng cạnh: client→Nginx, Nginx→HAProxy, HAProxy→A/B.
- Backend thấy **source IP = proxy**. IP client gốc truyền qua header `X-Forwarded-For` — chỉ tin khi đến từ proxy bạn kiểm soát.
- Client **không thấy** RST của backend; nó chỉ thấy status proxy trả (502...).

---

## 2. Nginx — các khối chính

```nginx
http {
    upstream app_pool {                 # nhóm backend
        server 127.0.0.1:18081;
        server 127.0.0.1:18082;
    }
    server {                            # virtual host
        listen 443 ssl;
        server_name app.lab;            # khớp SNI/Host
        ssl_certificate     /etc/nginx/lab/app.crt;
        ssl_certificate_key /etc/nginx/lab/app.key;

        location /api/ {                # khớp path
            proxy_pass http://app_pool;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_connect_timeout 3s;
            proxy_read_timeout 10s;
        }
    }
}
```

| Khối | Chọn theo |
|---|---|
| `server` | listener + `server_name` |
| `location` | path |
| `proxy_pass` | upstream nhận request |

Quy trình an toàn: `nginx -t` → `systemctl reload nginx` → đọc **access log** (request/status) + **error log** (`connect() failed`, `upstream timed out`).

## 3. HAProxy — các section

```haproxy
global
    log stdout format raw local0
defaults
    mode http
    timeout connect 3s
    timeout client  30s
    timeout server  30s
frontend fe_web
    bind :8080
    acl is_api path_beg /api
    use_backend be_api if is_api
    default_backend be_web
backend be_api
    balance roundrobin
    option httpchk GET /healthz
    server a 127.0.0.1:18081 check
    server b 127.0.0.1:18082 check
listen stats
    bind 127.0.0.1:8404
    stats enable
    stats uri /stats
```

| Section | Vai trò |
|---|---|
| `global` | Tham số process (log, maxconn) |
| `defaults` | Giá trị **kế thừa** cho các section sau |
| `frontend` | Listener + **ACL** + chọn backend |
| `backend` | Server, thuật toán cân bằng, health check |

| Khái niệm | Ý nghĩa |
|---|---|
| `mode tcp` | L4: chuyển dòng byte, không hiểu HTTP |
| `mode http` | L7: hiểu Host/path/status, chạy HTTP health check |
| `roundrobin` / `leastconn` | Chia lượt / ưu tiên server ít connection |
| `option httpchk` + `check` | **Active health check**: process còn chạy nhưng `/healthz` fail → bị loại |
| `timeout connect/client/server` | Giới hạn từng pha — đặt quá thấp ở `defaults` làm backend chậm bị coi là lỗi |
| ACL + `use_backend` | Điều kiện (Host/path) chọn backend — ACL sai đưa request sang backend khác dù TCP đều OK |

---

## 4. Health check và failover

```text
check OK  → server UP   → nhận traffic
check FAIL (đủ số lần) → server DOWN → traffic chuyển sang server còn UP
tất cả DOWN → client nhận 503 (HAProxy) / 502 (Nginx, tùy cấu hình)
```

**Chứng minh failover đúng** cần: response phân biệt được A/B + stats/log HAProxy cho thấy server DOWN + request mới chỉ tới server UP.

## 5. Khi client thấy 5xx

1. Ghi timestamp.
2. Xem response header — tầng nào trả?
3. Đọc log **từng tầng** cùng timestamp: Nginx access/error → HAProxy log/stats → app log.
4. Test từng cạnh trực tiếp (`curl` từ proxy tới backend).

> Trong lab, cert tự ký sẽ báo "not trusted" đúng thiết kế. Kiểm tên và validity; đừng dùng `-k` để tuyên bố HTTPS đạt.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Một request = một connection." | Qua proxy là nhiều connection. |
| "Backend thấy IP client." | Thấy IP proxy, trừ khi đọc `X-Forwarded-For`/PROXY protocol. |
| "Process app còn chạy là backend UP." | Health check HTTP mới quyết định. |
| "Reload nginx không cần test." | Luôn `nginx -t` / `haproxy -c -f` trước. |

## Tự kiểm tra

1. Client nhận 503, Nginx log ghi upstream trả 503, HAProxy stats: A, B đều DOWN. Lỗi ở tầng nào?
2. Backend thấy mọi request từ `127.0.0.1`. Có phải lỗi không?
3. Request `/api/x` tới `be_web` thay vì `be_api`. Kiểm gì?

<details>
<summary>Đáp án</summary>

1. 503 do HAProxy tạo (không có backend khỏe); điều tra vì sao health check A/B fail.
2. Không — đó là IP proxy; xem `X-Forwarded-For` nếu cần IP gốc.
3. ACL `path_beg /api` và thứ tự `use_backend`; Nginx có rewrite path không.

</details>

## Nguồn

[NGINX reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) · [HAProxy configuration manual](https://docs.haproxy.org/3.2/configuration.html) · [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)
