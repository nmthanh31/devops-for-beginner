# N06 Bài 1 — DHCP cấp cấu hình, DNS trả địa chỉ

> **Sau bài này bạn sẽ:**
> - Kể được 4 bước DORA và lease chứa gì.
> - Vẽ đường đi của một truy vấn DNS: app → NSS → stub → recursive → authoritative.
> - Phân biệt **NXDOMAIN**, **timeout**, **trả IP sai/cũ** — ba lỗi DNS khác nhau.
>
> **Cần trước:** [N05](../../domain05-RoutingReturnPath/README.md) (client cần route tới DNS server).

---

## 1. Hình dung

- **DHCP** = lễ tân phát thẻ cho nhân viên mới: số phòng (IP), lối ra (gateway), số tổng đài hỏi đáp (DNS). Thẻ có **hạn** (lease).
- **DNS** = danh bạ: đổi tên (`app.lab`) thành số (IP). Có danh bạ gốc (authoritative) và người tra hộ có trí nhớ ngắn hạn (recursive resolver + cache TTL).

## 2. DHCP — DORA

```text
Client (chưa có IP)                         DHCP server
  │── Discover  (broadcast) ────────────────►│  "có ai cấp IP không?"
  │◄──────────── Offer ──────────────────────│  "lấy 10.6.1.20 nhé"
  │── Request   (broadcast) ────────────────►│  "tôi chọn 10.6.1.20"
  │◄──────────── ACK ────────────────────────│  "xác nhận, lease 24h"
```

| Lease thường gồm | Ví dụ |
|---|---|
| IP / prefix | `10.6.1.20/24` |
| Default gateway | `10.6.1.1` |
| DNS server | `10.6.1.53` |
| Search domain | `lab` |
| Thời hạn | 86400s |

- Discover là **broadcast** (client chưa có IP). Server ở subnet khác → router cần **DHCP relay**.
- Lease phải gia hạn; đổi option trên server **không** hiện ngay trên client.
- Kiểm cấu hình **thực tế đang có**, không chỉ đọc cấu hình mong muốn ở server:

```bash
ip addr; ip route; resolvectl status
```

> DHCP thành công **không** chứng minh DNS server trả lời được.

---

## 3. DNS

### Record hay gặp

| Record | Nghĩa |
|---|---|
| `A` | Tên → IPv4 |
| `AAAA` | Tên → IPv6 |
| `CNAME` | Bí danh → tên khác |
| `PTR` | IP → tên (reverse) |

### Đường đi một truy vấn

```text
App (curl)
  → NSS (/etc/nsswitch.conf: "hosts: files dns")
      → files: /etc/hosts          ← có thể thắng DNS!
      → dns:   stub resolver (systemd-resolved 127.0.0.53)
                 → recursive resolver (10.6.1.53)  [cache theo TTL]
                      → authoritative server của zone
```

### Ba lỗi khác nhau

| Kết quả | Nghĩa | Hướng kiểm |
|---|---|---|
| `NXDOMAIN` | DNS **trả lời**: tên không tồn tại | Tên đúng chưa? Zone có record? |
| Timeout / `SERVFAIL` | Không có câu trả lời đúng hạn / server lỗi | Route/firewall tới DNS, server sống? |
| Trả IP sai / cũ | Có câu trả lời nhưng sai | Cache, TTL, dữ liệu authoritative, `/etc/hosts` |

### Hai công cụ, hai đường

| Lệnh | Đi qua | Dùng để |
|---|---|---|
| `getent ahosts NAME` | **NSS** (như ứng dụng thật) | Ứng dụng sẽ nhận gì |
| `dig NAME` | Chỉ DNS | DNS trả gì |
| `dig @10.6.1.53 NAME` | Một server cụ thể | So sánh từng resolver |

`getent` khác `dig` → nghi `/etc/hosts` hoặc thứ tự `hosts:` trong `nsswitch.conf`.

### TTL và cache

TTL 300s: resolver vừa cache record cũ có thể còn trả IP cũ gần 5 phút, trong khi resolver khác đã trả IP mới. "Máy A được, máy B chưa" sau khi đổi DNS **chưa chắc** là mạng chập chờn. Ứng dụng còn có thể giữ connection/cache riêng lâu hơn TTL.

Ghi evidence: thời điểm, server trả lời, TTL còn lại, kết quả `getent`.

```text
DHCP → cấu hình IP/gateway/DNS
DNS  → tên thành IP
route/TCP/TLS/HTTP → dùng IP đó
```

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Có IP từ DHCP là mạng ổn." | Còn route, DNS. |
| "`dig` OK thì app resolve OK." | App đi qua NSS (`/etc/hosts`...). |
| "Đổi DNS là có hiệu lực ngay." | Phải chờ TTL + cache ứng dụng. |
| "NXDOMAIN là DNS server chết." | Server sống và trả lời "không có". |

## Tự kiểm tra

1. `ping 10.6.1.30` OK, `ping app.lab` báo `Name or service not known`. Lỗi lớp nào?
2. `dig app.lab` trả `10.6.1.30`, `getent ahosts app.lab` trả `10.6.1.99`. Nghi gì?
3. `dig` báo `connection timed out; no servers could be reached`. Khác NXDOMAIN thế nào?

<details>
<summary>Đáp án</summary>

1. Phân giải tên (DNS/NSS), không phải route.
2. `/etc/hosts` có mapping `10.6.1.99` (NSS ưu tiên `files`).
3. Không nhận được câu trả lời → kiểm route/firewall/server; NXDOMAIN là có câu trả lời.

</details>

## Nguồn

[RFC 2131 DHCP](https://www.rfc-editor.org/rfc/rfc2131) · [RFC 1034 DNS](https://www.rfc-editor.org/rfc/rfc1034) · [LPIC-1 109.2/109.4](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
