# N05 — Routing & Return Path

> **Câu hỏi domain này trả lời:** Packet đi tới đích bằng đường nào, và quan trọng hơn — phản hồi có **quay về** được không?

**Mô hình cần nhớ một câu:** *Mỗi host tự quyết route của mình; chiều đi và chiều về là hai quyết định độc lập trên hai máy — luôn kiểm cả hai đầu.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [Route đi và route về](./docs/01-forward-and-return.md) | 40′ | Route gồm gì? Router Linux cần gì để forward? |
| 2 | [Bằng chứng lỗi route](./docs/02-route-diagnosis.md) | 45′ | Paired capture, asymmetric, policy routing |
| 3 | [Ví dụ: SYN-ACK đi sai đường](./docs/03-return-route-walkthrough.md) | 20′ | Định vị return path lỗi |
| 4 | [Lab: một chiều đúng, chiều về sai](./lab/01-two-way-route.md) | 75′ | Tái hiện, capture, sửa tối thiểu |

## Đạt domain khi bạn có thể

- [ ] Dựng client–router–server bằng namespace từ blank.
- [ ] Dùng `ip route get` (kể cả `from SRC`) ở cả hai đầu.
- [ ] Từ paired capture chỉ ra đoạn packet dừng.
- [ ] Giải thích asymmetric routing gây lỗi khi nào, và khi nào phải xem `ip rule`.

## Liên kết

- Trước: [N04](../domain04-NetnsVethBridgeVLAN/README.md) · Tiếp theo: [N06 DHCP, DNS & time](../domain06-DHCPDNSTime/README.md)

## Nguồn

[ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html) · [ip-rule(8)](https://man7.org/linux/man-pages/man8/ip-rule.8.html) · [LPIC-1 109.3](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
