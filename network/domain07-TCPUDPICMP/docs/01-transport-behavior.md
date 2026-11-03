# N07 Bài 1 — TCP connection, UDP datagram, ICMP message

> **Sau bài này bạn sẽ:**
> - Vẽ được three-way handshake và đóng kết nối, biết mỗi bước chứng minh gì.
> - Phân biệt **RST/refused** với **timeout** — hai triệu chứng dẫn tới hai hướng điều tra khác nhau.
> - Hiểu vì sao ping OK không có nghĩa là port mở, và vì sao UDP "gửi được" không có nghĩa là "tới nơi".
>
> **Cần trước:** [N01](../../domain01-EncapsulationEthernet/README.md) (port là địa chỉ của socket), [N05](../../domain05-RoutingReturnPath/README.md) (đường về).

---

## 1. Hình dung

| | Giống | Đặc điểm |
|---|---|---|
| **TCP** | Gọi điện thoại | Nhấc máy xác nhận trước (handshake), nói theo thứ tự, mất thì nói lại |
| **UDP** | Gửi bưu thiếp | Gửi là xong, không biết tới hay chưa, không thứ tự |
| **ICMP** | Thông báo của bưu điện | "Không có người nhận", "thư quá khổ" — không có số phòng (port) |

## 2. TCP

### 4-tuple

Một connection được nhận diện bằng `src IP, src port, dst IP, dst port`. Nhờ vậy một server `:443` phục vụ hàng nghìn client cùng lúc — mỗi client khác source.

### Three-way handshake

```text
Client                                   Server (LISTEN :8080)
  │── SYN (seq=x) ───────────────────────►│   client: SYN-SENT
  │◄──────────────── SYN-ACK (seq=y,ack=x+1)│  server: SYN-RECV
  │── ACK (ack=y+1) ─────────────────────►│   cả hai: ESTABLISHED
  │══════════ dữ liệu (dòng byte) ════════│
```

`connect()` thành công chứng minh **TCP tới được listener** — chưa chứng minh TLS/HTTP đúng.

### Các cơ chế khác

- **Sequence/ACK**: đánh số byte, xác nhận đã nhận.
- **Retransmit**: gửi lại sau timeout hoặc duplicate ACK. Nhiều retransmission có thể do loss, congestion — hoặc capture thấy bản sao. Cần timestamp, seq, RTT và capture hai đầu ([N10](../../domain10-LossMTU/README.md)).
- **Receiver window**: bảo vệ bên nhận khỏi bị ngập. **Congestion control**: điều chỉnh theo đường truyền.
- TCP truyền **dòng byte**, không biết "một HTTP response" kết thúc ở đâu — ứng dụng tự xác định.

### Đóng kết nối

| Kiểu | Gói | Ý nghĩa |
|---|---|---|
| Bình thường | FIN / ACK | Đóng có trật tự. Bên đóng trước vào **TIME-WAIT** (chống nhầm packet cũ) — **không phải lỗi** |
| Đột ngột | **RST** | Từ chối hoặc hủy ngay |

## 3. Refused vs Timeout — quan trọng nhất bài

```text
"Connection refused"                    "Connection timed out"
Client ── SYN ──► Server                Client ── SYN ──► ???
Client ◄── RST ── Server                Client ── SYN ──► ??? (gửi lại)
                                        Client ── SYN ──► ??? ... hết giờ
```

| | Refused | Timeout |
|---|---|---|
| Client nhận được | **RST** (hoặc ICMP unreachable) | **Không gì cả** |
| Chứng minh | Packet **tới** được ai đó, họ từ chối | Chưa biết packet/response mất ở đâu |
| Nguyên nhân hay gặp | Không có listener; firewall `reject` | Firewall `drop`; route đi/về; host down |
| Kiểm tiếp | `ss -lntp` trên server, bind address | Paired capture client + server |

> Refused thường **tốt hơn** timeout để chẩn đoán: ít nhất bạn biết đường đi tới đó thông suốt. Capture cho biết *ai* gửi RST (server hay firewall ở giữa).

## 4. Listener và bind address

| Bind | Nhận từ |
|---|---|
| `127.0.0.1:8080` | Chỉ loopback **trong namespace đó** |
| `10.7.0.20:8080` | Chỉ IP đó |
| `0.0.0.0:8080` | Mọi IPv4 local (nếu firewall/path cho phép) |
| `[::]:8080` | Mọi IPv6 (thường cả IPv4 tùy `bindv6only`) |

Client thường để kernel chọn **source port tạm thời**.

## 5. UDP

- Không handshake; `ss -u` không có `ESTAB` kiểu TCP.
- Gửi datagram **không chứng minh** bên kia nhận/trả lời.
- Đích không có socket → thường trả **ICMP Port Unreachable**.
- DNS thường dùng UDP/53, nhưng có thể chuyển sang TCP/53 (response lớn).

## 6. ICMP

Mang thông báo mạng: **Echo Request/Reply** (ping), **Destination Unreachable** (host/port/admin prohibited), **Time Exceeded** (TTL=0, dùng bởi traceroute), **Packet Too Big/Fragmentation Needed** (PMTUD, N10). ICMP **không có port**.

> Ping thành công chỉ chứng minh ICMP có phản hồi. Port ứng dụng có thể vẫn đóng, và ngược lại firewall có thể chặn ping mà web vẫn chạy.

---

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Ping được thì web phải chạy." | Khác protocol, khác rule. |
| "Nhiều TIME-WAIT là server lỗi." | Bình thường sau khi đóng kết nối. |
| "Timeout nghĩa là server down." | Có thể firewall drop hoặc đường về sai. |
| "UDP gửi thành công là tới nơi." | UDP không xác nhận. |

## Tự kiểm tra

1. Capture client thấy SYN gửi 3 lần, không có gì quay về. Đây là refused hay timeout? Bước tiếp?
2. Server `ss -lntp` hiện `127.0.0.1:8080`. Client từ máy khác báo gì?
3. Vì sao server cùng port 443 có thể phục vụ nhiều client?

<details>
<summary>Đáp án</summary>

1. Timeout. Capture ở server: thấy SYN không? Có trả SYN-ACK không? Kiểm return route.
2. Thường `Connection refused` (kernel trả RST vì không có socket khớp IP đích), trừ khi firewall drop trước.
3. Mỗi connection khác 4-tuple (source IP/port khác nhau).

</details>

## Nguồn

[RFC 9293 TCP](https://www.rfc-editor.org/rfc/rfc9293) · [RFC 768 UDP](https://www.rfc-editor.org/rfc/rfc768) · [RFC 792 ICMP](https://www.rfc-editor.org/rfc/rfc792)
