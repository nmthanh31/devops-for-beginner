# N11 — OSPF & VPN

> **Câu hỏi domain này trả lời:** Router học route tự động thế nào, tunnel mã hóa nối hai site ra sao — và vì sao "trạng thái xanh" vẫn có thể không có traffic?

**Mô hình cần nhớ một câu:** *Control plane (neighbor Full, handshake) xanh chưa chứng minh data plane; luôn đi tiếp tới route trong kernel, AllowedIPs, return path và packet thật.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [OSPF adjacency](./docs/01-ospf-adjacency.md) | 40′ | Hello → Full → LSDB → SPF → kernel route; kẹt state nào nghi gì |
| 2 | [WireGuard tunnel](./docs/02-wireguard-tunnel.md) | 40′ | Underlay vs overlay, AllowedIPs, đọc `wg show` |
| 3 | [Ví dụ: control xanh, data đỏ](./docs/03-ospf-vpn-walkthrough.md) | 15′ | Kiểm theo lớp |
| 4 | [Lab: tunnel & adjacency](./lab/01-adjacency-and-tunnel-evidence.md) | 120′ | WireGuard trong namespace, OSPF với FRR |

## Đạt domain khi bạn có thể

- [ ] Sửa một OSPF fault (area/MTU) trong FRR và chứng minh bằng adjacency + route + ping.
- [ ] Dựng WireGuard hai peer, giải thích handshake vs inner traffic.
- [ ] Capture underlay và `wg0`, giải thích khác biệt.
- [ ] Nói được BGP khác OSPF ở điểm nào (policy giữa tổ chức).

## Liên kết

- Trước: [N10](../domain10-LossMTU/README.md) · Tiếp theo: [N12 Cloud & K8s](../domain12-CloudK8sNetwork/README.md)

## Nguồn

[FRR OSPFv2](https://docs.frrouting.org/en/latest/ospfd.html) · [RFC 2328](https://www.rfc-editor.org/rfc/rfc2328) · [WireGuard Quick Start](https://www.wireguard.com/quickstart/)
