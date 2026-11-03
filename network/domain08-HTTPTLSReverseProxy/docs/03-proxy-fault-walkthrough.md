# N08 Ví dụ — TLS lỗi, upstream lỗi, app 404

Client gọi `https://api.lab/healthz`. DNS trả proxy `10.8.0.10`. Backend `10.8.1.20:8080`.

> ✋ Với mỗi trường hợp, đoán: client thấy gì, proxy log có gì, backend log có gì.

| | Cert mismatch | Upstream refused | Backend 404 |
|---|---|---|---|
| Client thấy | Lỗi TLS, **không** có status | `502` | `404` |
| Bước dừng | ③ TLS | ④ proxy → backend | ⑤ app |
| Proxy access log | Thường **không** có request | Có, status 502 | Có, status 404 |
| Proxy error log | (có thể có SSL handshake) | `connect() failed (111: Connection refused)` | — |
| Backend log | Không | Không | Có request `/healthz` → 404 |

## 1. Certificate name mismatch

TCP tới `:443` OK. Proxy đưa cert cho `other.lab`, client yêu cầu `api.lab` (SNI). Client dừng **trước** khi gửi HTTP.

```bash
curl -v https://api.lab/healthz
curl -v --resolve api.lab:443:10.8.0.10 https://api.lab/healthz
```

Cả hai đều lỗi TLS → không phải DNS. `--resolve` chỉ bỏ qua DNS, vẫn giữ SNI/Host.

**Fix:** đúng cert/`server_name` cho `api.lab`.

## 2. Upstream connection refused

TLS client↔proxy OK. Proxy gửi tới `10.8.1.20:8080`, backend không listen → RST **cho proxy** → proxy trả **502** cho client. Client không thấy RST đó (hai connection khác nhau).

**Fix:** khởi động/sửa bind backend. Verify: `curl` từ proxy tới backend trực tiếp, rồi từ client.

## 3. Backend trả 404

Backend nhận request nhưng không có route `/healthz`; proxy chuyển 404 về. Kiểm path rewrite ở proxy (`proxy_pass` có/không dấu `/` cuối thay đổi path!) và route của app.

404 **không** chứng minh DNS/TLS sai.

---

**Evidence chuẩn:** timestamp + `curl -v` + proxy log + backend log → đặt lỗi đúng vào chuỗi DNS → TCP → TLS → HTTP → upstream.
