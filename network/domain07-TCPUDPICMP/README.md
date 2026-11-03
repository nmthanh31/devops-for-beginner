# N07 — TCP, UDP & ICMP

> **Câu hỏi domain này trả lời:** Packet đã tới host — vậy nó có tới được **socket** không, và triệu chứng `refused` / `timeout` / `404` nói lên điều gì?

**Mô hình cần nhớ một câu:** *RST = có người từ chối (đường tới thông); timeout = không ai trả lời (chưa biết mất ở đâu); 404 = mạng ổn, app trả lời.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [TCP, UDP, ICMP](./docs/01-transport-behavior.md) | 45′ | Handshake, refused vs timeout, bind address |
| 2 | [Socket state & capture](./docs/02-state-and-capture.md) | 40′ | Đọc `ss` và cờ TCP, kết luận đúng lớp |
| 3 | [Ví dụ: ba kiểu không vào được web](./docs/03-connection-fault-walkthrough.md) | 15′ | Refused / timeout / 404 |
| 4 | [Lab: bind, handshake, refused](./lab/01-port-and-handshake.md) | 60′ | Thấy RST và handshake thật |

## Đạt domain khi bạn có thể

- [ ] Map socket ↔ process bằng `ss -lntp`.
- [ ] Đọc handshake, FIN, RST trong `tcpdump`.
- [ ] Phân biệt refused vs timeout và chọn bước điều tra tương ứng.
- [ ] Giải thích TIME-WAIT, CLOSE-WAIT, SYN-RECV.
- [ ] Tích lũy dần 6 pcap có chú thích (yêu cầu competency N07).

## Liên kết

- Trước: [N06](../domain06-DHCPDNSTime/README.md) · Tiếp theo: [N08 HTTP, TLS & reverse proxy](../domain08-HTTPTLSReverseProxy/README.md)

## Nguồn

[RFC 9293 TCP](https://www.rfc-editor.org/rfc/rfc9293) · [RFC 768 UDP](https://www.rfc-editor.org/rfc/rfc768) · [RFC 792 ICMP](https://www.rfc-editor.org/rfc/rfc792)
