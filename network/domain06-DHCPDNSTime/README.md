# N06 — DHCP, DNS & Time

> **Câu hỏi domain này trả lời:** Máy lấy cấu hình mạng từ đâu, đổi tên thành IP thế nào, và vì sao đồng hồ sai lại làm hỏng HTTPS?

**Mô hình cần nhớ một câu:** *DHCP cấp cấu hình → DNS đổi tên ra IP → clock đúng để TLS tin cert; mỗi bước PASS không làm bước sau tự PASS.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [DHCP & DNS](./docs/01-dhcp-dns.md) | 45′ | DORA, đường đi DNS, NXDOMAIN vs timeout vs IP cũ |
| 2 | [Thời gian & phân loại lỗi](./docs/02-time-and-resolution-diagnosis.md) | 35′ | UTC/timezone/sync, clock lệch phá TLS |
| 3 | [Ví dụ: có IP mà HTTPS lỗi](./docs/03-dhcp-dns-time-walkthrough.md) | 15′ | Tách DHCP / DNS / clock |
| 4 | [Lab: lease, DNS, clock](./lab/01-lease-dns-clock.md) | 60′ | Đọc cấu hình thật, so getent/dig |

## Đạt domain khi bạn có thể

- [ ] Tách NXDOMAIN / timeout / stale / wrong answer bằng evidence.
- [ ] Giải thích vì sao `getent` khác `dig`.
- [ ] Dùng `curl --resolve` để tách DNS khỏi TLS/backend.
- [ ] Đọc `timedatectl` và so validity cert với `date -u`.

## Liên kết

- Trước: [N05](../domain05-RoutingReturnPath/README.md) · Tiếp theo: [N07 TCP, UDP & ICMP](../domain07-TCPUDPICMP/README.md)

## Nguồn

[RFC 2131 DHCP](https://www.rfc-editor.org/rfc/rfc2131) · [RFC 1034 DNS](https://www.rfc-editor.org/rfc/rfc1034) · [LPIC-1 108.1, 109.2, 109.4](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
