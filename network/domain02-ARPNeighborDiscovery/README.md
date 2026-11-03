# N02 — ARP & Neighbor Discovery

> **Câu hỏi domain này trả lời:** Đã biết IP next hop, làm sao host biết MAC để đóng frame — và khi việc đó thất bại thì trông như thế nào?

**Mô hình cần nhớ một câu:** *Route chọn next hop trước; ARP (IPv4) / ND (IPv6) hỏi MAC của next hop sau; broadcast/multicast đó chỉ vang trong một broadcast domain.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [ARP và neighbor cache](./docs/01-arp-and-neighbor-cache.md) | 40′ | ARP hỏi IP nào? Các trạng thái neighbor nghĩa là gì? |
| 2 | [IPv6 ND và chẩn đoán](./docs/02-ipv6-nd-and-diagnosis.md) | 40′ | ND khác ARP ra sao? Đọc capture request/reply thế nào? |
| 3 | [Ví dụ: route đúng nhưng ARP fail](./docs/03-neighbor-fault-walkthrough.md) | 20′ | Điều tra theo thứ tự nào? |
| 4 | [Lab: ai được ARP hỏi](./lab/01-neighbor-evidence.md) | 60′ | Chứng minh và tạo lỗi prefix |

## Đạt domain khi bạn có thể

- [ ] Từ output `ip route get`, nói đúng IP sẽ bị ARP hỏi.
- [ ] Giải thích `REACHABLE`/`STALE`/`FAILED` và điều mỗi trạng thái *không* chứng minh.
- [ ] Lọc capture đúng cho IPv4 và IPv6 (`arp or icmp6`).
- [ ] Từ capture request/reply, khoanh vùng lỗi: interface / L2-VLAN / IP đích / duplicate.

## Liên kết

- Trước: [N01 Encapsulation & Ethernet](../domain01-EncapsulationEthernet/README.md)
- Tiếp theo: [N03 CIDR & Subnetting](../domain03-CIDRSubnetting/README.md)

## Nguồn

[RFC 826 ARP](https://www.rfc-editor.org/rfc/rfc826) · [RFC 4861 IPv6 ND](https://www.rfc-editor.org/rfc/rfc4861) · [ip-neighbour(8)](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html)
