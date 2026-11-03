# W7 Lab chính — Client → router → DNS → Nginx TLS → HAProxy → hai backend

| | |
|---|---|
| **Thời lượng** | S2 guided + S4 independent (~4–5h) + S5 gate 90′ |
| **Cần trước** | [N05](../domain05-RoutingReturnPath/README.md)–[N08](../domain08-HTTPTLSReverseProxy/README.md), đặc biệt [lab N08](../domain08-HTTPTLSReverseProxy/lab/01-trace-web-path.md) |
| **Gate** | 8 fault — đúng ≥ 7, sửa ≥ 6 |

> **Trước khi bắt đầu:** viết address plan (bảng prefix/gateway/route về) và một bảng "cạnh → IP:port → protocol" cho cả 3 chặng. Không có hai bảng này thì chưa dựng.

## Mục tiêu

Tạo đường đi hai chiều và chứng minh từng lớp từ tên miền đến HTTP response. Topology có thể dựng trên nhiều VM hoặc namespace/containers lab; dùng địa chỉ riêng không trùng VMware/VPN hiện có.

```text
client ─ router ─ Nginx:443 ─ HAProxy:8081 ─ backend A:8080
          │                                └ backend B:8080
          └ DNS/NTP service lab hoặc dịch vụ test được phép dùng
```

## Thứ tự triển khai

1. Vẽ address plan, route đi và route về. Chứng minh `ip route get` ở cả client/proxy/backends.
2. Xác định DNS record của tên lab và resolver của client; dùng `getent` và `dig` so kết quả.
3. Bật hai backend với endpoint `/healthz` trả `200` và response header/body khác nhau để phân biệt A/B. Kiểm `ss` và `curl` trực tiếp trước khi thêm proxy.
4. Cấu hình HAProxy frontend/backend ở `mode http`, cân bằng `roundrobin` và active health check `/healthz`. Test trực tiếp frontend; dừng A và chứng minh request mới đi B sau khi A bị đánh dấu down. Đọc log/stats của HAProxy.
5. Cấu hình Nginx `server` cho lab hostname, TLS certificate, `location` và `proxy_pass` tới HAProxy. Chuyển Host và header client phù hợp. Kiểm `nginx -t` trước reload. Test bằng `curl -v --resolve NAME:443:NGINX_IP https://NAME/healthz`.
6. Tạo thêm một Host/path rule lab để chứng minh request được chọn đúng route. Kiểm response cho Host/path đúng và một negative test cho Host/path không khớp. Ghi timestamp/timezone/NTP status để khi so log các máy không nhầm giờ.

Nginx terminate TLS rồi tạo HTTP connection mới đến HAProxy; HAProxy lại tạo connection tới backend. Vì có ba chặng, hãy ghi IP:port, listener và HTTP status cho **từng cạnh**. Nếu môi trường lab cần HTTPS giữa Nginx và HAProxy, ghi thêm TLS ở cạnh đó; đừng mặc định TLS ngoài cùng bảo vệ mọi chặng.

Nếu dùng certificate tự ký, cài CA lab vào trust store của client lab hoặc chỉ rõ test nào đang xác minh certificate và test nào dùng tạm `-k` để cô lập lỗi. Không ghi “TLS PASS” dựa vào `-k`.

## Break/fix

Tạo từng lỗi: thiếu return route, DNS record/TTL sai, listener bind loopback, TCP refused so với timeout, SNI/certificate name mismatch, Nginx upstream sai, HAProxy backend down hoặc health path sai, Host/path rule sai. Với lỗi 502/503, ghi **Nginx hay HAProxy** là thành phần trả status bằng access/error log. Mỗi lỗi phải có prediction, evidence ở hai vị trí và fix nhỏ nhất.

## Evidence và gate

Nộp route tables, DNS answer, `ss`, `nginx -t`, `curl -v`/certificate, paired captures, Nginx access/error log, HAProxy log/stats, backend log, positive + negative health tests. Gate Calendar: 8 fault, đúng ít nhất 7, sửa ít nhất 6. Ghi cleanup và rollback config của từng thành phần lab. So sánh thêm một flow client→HAProxy trực tiếp để giải thích Nginx thêm TLS/virtual host ở đâu.

### Mẫu scorecard (mỗi fault một dòng)

| # | Fault (người khác tạo / tự tạo mù) | Hypothesis trước lệnh | Evidence lớp 1 | Evidence lớp 2 | Root cause | Fix tối thiểu | Positive | Negative | Đúng? | Sửa? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | |

Nguồn: [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110), [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446), [NGINX reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/), [HAProxy configuration manual](https://docs.haproxy.org/3.2/configuration.html).
