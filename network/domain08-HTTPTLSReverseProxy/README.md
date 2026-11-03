# N08 — HTTP, TLS & Reverse Proxy

> **Câu hỏi domain này trả lời:** Khi web lỗi, lỗi nằm ở DNS, TCP, TLS, proxy hay backend — và tầng nào đã tạo ra status 502/503/404?

**Mô hình cần nhớ một câu:** *DNS → TCP → TLS (SNI, cert) → HTTP (Host, path) → upstream; qua proxy là nhiều connection độc lập, mỗi tầng có log riêng.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [HTTP & TLS](./docs/01-http-tls.md) | 45′ | Status nghĩa gì, TLS kiểm gì, SNI vs Host |
| 2 | [Proxy & backend](./docs/02-proxy-backends.md) | 60′ | Nginx/HAProxy config, health check, ACL, timeout |
| 3 | [Ví dụ: TLS vs upstream vs 404](./docs/03-proxy-fault-walkthrough.md) | 20′ | Đặt lỗi vào đúng tầng |
| 4 | [Lab: HTTPS → proxy → 2 backend](./lab/01-trace-web-path.md) | 90′ | Dựng, tạo 2 lỗi, đọc log |

Lab tuần: [W7 routed HTTPS application](../weekly-labs/W7-routing-to-application.md) (Nginx + HAProxy đầy đủ).

## Đạt domain khi bạn có thể

- [ ] Chú thích `curl -v` theo từng bước DNS/TCP/TLS/HTTP.
- [ ] Dùng `--resolve` và `openssl s_client -servername` để tách DNS và cert.
- [ ] Viết Nginx `server/location/upstream/proxy_pass` và HAProxy `frontend/backend/acl/httpchk` từ trí nhớ.
- [ ] Sửa 502/503/cert/timeout bằng log hai tầng.

## Liên kết

- Trước: [N07](../domain07-TCPUDPICMP/README.md) · Tiếp theo: [N09 Firewall, conntrack & NAT](../domain09-FirewallConntrackNAT/README.md)

## Nguồn

[RFC 9110 HTTP](https://www.rfc-editor.org/rfc/rfc9110) · [RFC 8446 TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446) · [NGINX reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) · [HAProxy manual](https://docs.haproxy.org/3.2/configuration.html)
