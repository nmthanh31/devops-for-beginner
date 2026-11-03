# N07 Ví dụ — Ba kiểu "không vào được web"

Client gọi `http://10.7.0.20:8080/healthz`.

> ✋ Với mỗi trường hợp, đoán packet trong capture **trước** khi đọc phân tích.

| | Refused | Timeout | 404 |
|---|---|---|---|
| Client thấy | `Connection refused` | `timed out` | `HTTP/1.1 404` |
| Capture | SYN → **RST** | SYN, SYN, SYN… | Handshake + HTTP request/response |
| Lớp lỗi | Transport tại server | Chưa biết — trên đường | Application |

## Trường hợp 1 — Connection refused

Server nhận SYN nhưng không có socket khớp `10.7.0.20:8080` → kernel trả RST.

```bash
ss -lntp | grep 8080
# LISTEN 0 128 127.0.0.1:8080 ...    ← bind loopback, không khớp 10.7.0.20
```

**Fix:** đổi bind sang `0.0.0.0` hoặc `10.7.0.20` (cấu hình app), không sửa route.

## Trường hợp 2 — Timeout

Client gửi SYN nhiều lần, không có SYN-ACK/RST.

| Capture server | Nghi |
|---|---|
| Không thấy SYN | Path / firewall **trước** server |
| Thấy SYN, không trả lời | Firewall INPUT (drop) trên server |
| Thấy SYN, trả SYN-ACK | **Đường về** ([N05](../../domain05-RoutingReturnPath/README.md)) |

## Trường hợp 3 — HTTP 404

Handshake xong, ứng dụng trả 404. Mạng đã đưa request tới **một** HTTP server. Kiểm Host header, path, proxy route, handler.

> 404 từ **nhầm server** vẫn có thể do DNS/LB trỏ sai → luôn ghi **IP đích** và **Host** khi phân tích.

```text
refused → TCP bị từ chối ở đích
timeout → chưa biết packet/response mất ở đâu
404     → HTTP server/proxy đã trả lời
```
