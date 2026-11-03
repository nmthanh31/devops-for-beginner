# N09 — Firewall, Conntrack & NAT

> **Câu hỏi domain này trả lời:** Rule nào quyết định packet qua hay bị chặn, và địa chỉ thay đổi thế nào khi đi qua NAT?

**Mô hình cần nhớ một câu:** *Chọn đúng hook (input/forward/output); stateful firewall cần cho chiều về; NAT dịch theo conntrack nên reply phải quay qua đúng thiết bị.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [nftables & conntrack](./docs/01-firewall-conntrack.md) | 45′ | Hook nào, rule order, state, drop vs reject |
| 2 | [NAT & bằng chứng](./docs/02-nat-and-evidence.md) | 40′ | SNAT/DNAT, tuple trước/sau NAT |
| 3 | [Ví dụ: firewall + SNAT](./docs/03-nat-walkthrough.md) | 15′ | Phân biệt hai lỗi cùng triệu chứng timeout |
| 4 | [Lab: filter & NAT](./lab/01-isolated-filter-nat.md) | 90′ | Ruleset stateful, masquerade, capture hai phía |

## Đạt domain khi bạn có thể

- [ ] Viết nftables policy forward stateful từ trí nhớ.
- [ ] Chọn đúng chain cho một flow cho trước.
- [ ] Chỉ ra tuple trước/sau NAT bằng capture + conntrack.
- [ ] Có positive/negative matrix cho ruleset.

## Liên kết

- Trước: [N08](../domain08-HTTPTLSReverseProxy/README.md) · Tiếp theo: [N10 Loss & MTU](../domain10-LossMTU/README.md)

## Nguồn

[nftables quick reference](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes) · [Connection tracking](https://wiki.nftables.org/wiki-nftables/index.php/Connection_Tracking_System) · [Ubuntu firewall](https://ubuntu.com/server/docs/firewalls/)
