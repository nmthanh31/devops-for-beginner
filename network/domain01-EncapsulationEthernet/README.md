# N01 — Encapsulation & Ethernet

> **Câu hỏi domain này trả lời:** Khi một request rời máy, nó được đóng gói ra sao, và mỗi chặng mạng thay đổi phần nào của nó?

**Mô hình cần nhớ một câu:** *MAC lo chặng hiện tại, IP lo đích cuối, port lo ứng dụng — MAC đổi mỗi hop, IP và port giữ nguyên (trừ NAT/proxy).*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [Các lớp và đóng gói](./docs/01-layers-and-frames.md) | 45′ | Vì sao cần cả MAC, IP, port? Lỗi nằm ở lớp nào? |
| 2 | [Switch và đọc capture](./docs/02-switch-and-capture.md) | 40′ | Switch học MAC thế nào? Đọc `tcpdump -e` ra sao? |
| 3 | [Ví dụ: request qua gateway](./docs/03-worked-packet.md) | 20′ | Header đổi gì ở mỗi link? |
| 4 | [Lab: quan sát đóng gói](./lab/01-observe-packet.md) | 60′ | Chứng minh dự đoán bằng capture thật |

## Đạt domain khi bạn có thể

- [ ] Vẽ đóng gói/tháo gói của một HTTP request, nêu trường dùng để demux ở mỗi lớp (EtherType, protocol, port).
- [ ] Dự đoán đúng MAC/IP/port/TTL trên hai link của một đường đi qua router.
- [ ] Đọc một dòng `tcpdump -eni` và tách thành 3 lớp.
- [ ] Từ thông báo lỗi (`resolve`, `timeout`, `refused`, `404`) chỉ ra lớp cần kiểm tiếp.

## Liên kết

- Nền tảng: [L10 Host Networking](../../linux/domain10-HostNetworking/docs/01-host-network-flow.md)
- Tiếp theo: [N02 ARP & Neighbor Discovery](../domain02-ARPNeighborDiscovery/README.md)

## Nguồn

[RFC 791 IPv4](https://www.rfc-editor.org/rfc/rfc791) · [RFC 9293 TCP](https://www.rfc-editor.org/rfc/rfc9293) · [Linux bridge documentation](https://docs.kernel.org/networking/bridge.html)
