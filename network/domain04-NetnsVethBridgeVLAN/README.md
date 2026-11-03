# N04 — Namespace, veth, bridge & VLAN

> **Câu hỏi domain này trả lời:** Làm sao dựng nhiều "máy" và "switch" trên một VM, và VLAN chia broadcast domain như thế nào?

**Mô hình cần nhớ một câu:** *Namespace = máy, veth = dây, bridge = switch, VLAN = chia switch thành nhiều switch logic; route/neighbor/FDB là ba bảng trả lời ba câu hỏi khác nhau.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [Network namespace & veth](./docs/01-netns-veth.md) | 35′ | Namespace chứa gì? Chạy lệnh đúng namespace thế nào? |
| 2 | [Bridge, FDB & VLAN](./docs/02-bridge-vlan.md) | 50′ | Access/trunk, PVID/untagged? Ba bảng khác nhau ra sao? |
| 3 | [Ví dụ: cùng bridge, khác VLAN](./docs/03-vlan-walkthrough.md) | 20′ | Frame đi qua bridge có VLAN thế nào? Lỗi PVID trông ra sao? |
| 4 | [Lab: topology cô lập](./lab/01-isolated-topology.md) | 75′ | Dựng từ blank, break/fix một port |

Sau đó làm lab tuần: [W6 hai VLAN](../weekly-labs/W6-l2-l3-foundation.md) (có [hướng dẫn từng bước](../weekly-labs/W6-guided-topology.md)).

## Đạt domain khi bạn có thể

- [ ] Dựng 2 namespace + bridge từ blank không cần notes.
- [ ] Nói đúng lệnh nào phải chạy với `ip -n` / `ip netns exec`.
- [ ] Phân biệt route / neighbor / FDB và lệnh xem từng bảng.
- [ ] Cấu hình access port (`vid N pvid untagged`) và chứng minh VLAN isolation **đúng cách** (cùng prefix, khác VLAN).

## Liên kết

- Trước: [N03 CIDR & Subnetting](../domain03-CIDRSubnetting/README.md)
- Tiếp theo: [N05 Routing & return path](../domain05-RoutingReturnPath/README.md)

## Nguồn

[ip-netns(8)](https://man7.org/linux/man-pages/man8/ip-netns.8.html) · [ip-link(8)](https://man7.org/linux/man-pages/man8/ip-link.8.html) · [bridge(8)](https://man7.org/linux/man-pages/man8/bridge.8.html) · [Linux bridge docs](https://docs.kernel.org/networking/bridge.html)
