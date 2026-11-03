# N08 Bài 1 — HTTP request, TLS và certificate

> **Sau bài này bạn sẽ:**
> - Đọc được cấu trúc HTTP request/response và vai trò của `Host`.
> - Hiểu TLS kiểm gì (chain, SAN, thời hạn) và **SNI** xảy ra trước HTTP.
> - Dùng `curl -v` và `curl --resolve` để biết lỗi ở bước DNS / TCP / TLS / HTTP.
>
> **Cần trước:** [N06](../../domain06-DHCPDNSTime/README.md), [N07](../../domain07-TCPUDPICMP/README.md).

---

## 1. Chuỗi bước của một HTTPS request

```text
① DNS        app.lab → 10.8.0.10
② TCP        handshake tới 10.8.0.10:443
③ TLS        ClientHello (SNI=app.lab) → cert → kiểm chain/SAN/thời hạn → khóa phiên
④ HTTP       GET /healthz  Host: app.lab   (đi BÊN TRONG kênh TLS)
⑤ Response   HTTP/1.1 200 OK
```

Lỗi ở bước nào thì các bước sau **không xảy ra**. Đây là chìa khóa đọc log.

## 2. HTTP

```text
GET /healthz HTTP/1.1          ← method, target/path, version
Host: app.lab                  ← tên site (HTTP/2: :authority)
User-Agent: curl/8.5
                               ← (body nếu có)

HTTP/1.1 200 OK                ← status
Content-Type: text/plain
ok
```

- **Host** cho phép nhiều site chung một IP:443 — proxy chọn **virtual host** theo tên.
- Path `/healthz` được Nginx chọn bằng `location`.
- `200` trên `/` **không** chứng minh `/healthz` đúng — test đúng endpoint mà LB/monitoring gọi.

### Status cần thuộc

| Status | Ý nghĩa | Ai thường trả |
|---|---|---|
| `200` | Thành công | App |
| `301/302` | Chuyển hướng | App/proxy |
| `404` | Không có resource | App (hoặc proxy không khớp location) |
| `502 Bad Gateway` | Proxy không nhận được response hợp lệ từ upstream (refused, reset, protocol sai) | **Proxy** |
| `503 Service Unavailable` | Không sẵn sàng / không có backend khỏe | Proxy **hoặc** app |
| `504 Gateway Timeout` | Upstream trả lời quá chậm | **Proxy** |

> Khi thấy 5xx, luôn hỏi **thành phần nào tạo ra status đó** — xem response header (`Server:`) và log từng tầng.

---

## 3. TLS

TLS cung cấp **mã hóa** + **xác thực server** (và toàn vẹn). Client kiểm certificate:

| Kiểm | Lỗi nếu sai |
|---|---|
| Chain tới CA tin cậy | `unable to get local issuer certificate` / self-signed |
| Tên trong **SAN** khớp tên client yêu cầu | `no alternative certificate subject name matches` |
| Thời hạn `notBefore`–`notAfter` | `not yet valid` / `expired` (xem clock — [N06](../../domain06-DHCPDNSTime/docs/02-time-and-resolution-diagnosis.md)) |

### SNI vs Host

| | SNI | Host header |
|---|---|---|
| Ở đâu | TLS ClientHello (bước ③) | HTTP request (bước ④) |
| Dùng để | Server chọn **certificate** | Server chọn **virtual host/app** |

Hai giá trị thường giống nhau. `curl https://10.8.0.10/` gửi SNI là IP → cert thường không khớp.

## 4. Công cụ

```bash
curl -v https://app.lab/healthz
# * Trying 10.8.0.10:443...        ← DNS + TCP
# * SSL connection using TLSv1.3   ← TLS OK
# * subject: CN=app.lab            ← cert
# > GET /healthz HTTP/1.1          ← HTTP request
# < HTTP/1.1 200 OK                ← response

curl -v --resolve app.lab:443:10.8.0.10 https://app.lab/healthz
#   ép IP (bỏ qua DNS) nhưng GIỮ hostname cho SNI + Host

openssl s_client -connect 10.8.0.10:443 -servername app.lab </dev/null
#   xem cert chain, subject, SAN, dates
```

> `curl -k` chỉ dùng **tạm** để tách lỗi cert khỏi lỗi khác — **không phải fix**.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Gọi bằng hostname mà lỗi là DNS." | Nếu `curl -v` đã qua `Trying IP` và TLS, DNS đã xong. |
| "502 là backend lỗi code." | Thường là proxy **không kết nối được** backend. |
| "TLS lỗi thì proxy log có request." | TLS fail → HTTP chưa diễn ra → access log có thể trống. |
| "`-k` chạy được là HTTPS ổn." | `-k` tắt xác thực. |

## Tự kiểm tra

1. `curl -v` dừng ở `SSL certificate problem: certificate has expired`. Đã qua những bước nào?
2. Proxy trả 502, app log không có gì. Nghi gì đầu tiên?
3. Vì sao `curl https://IP/` thường báo lỗi tên cert?

<details>
<summary>Đáp án</summary>

1. DNS, TCP, một phần TLS (đã nhận cert). HTTP chưa gửi.
2. Proxy không kết nối được backend (backend không listen / sai port / firewall) — request chưa tới app.
3. SNI/tên kiểm là IP, không có trong SAN của cert.

</details>

## Nguồn

[RFC 9110 HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) · [RFC 8446 TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
