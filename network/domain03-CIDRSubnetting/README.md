# N03 — CIDR & Subnetting

> **Câu hỏi domain này trả lời:** Với một IP/prefix, host coi đích nào là "hàng xóm" và đích nào phải qua gateway — và làm sao thiết kế dải địa chỉ không đụng nhau?

**Mô hình cần nhớ một câu:** *Prefix quyết định on-link; mỗi host tự quyết theo prefix của chính nó; khi nhiều route khớp, prefix dài nhất thắng.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [CIDR: tính bằng bit](./docs/01-cidr-calculation.md) | 45′ | Network/broadcast/host range của một IP/prefix? |
| 2 | [Address plan & overlap](./docs/02-address-plan-and-overlap.md) | 40′ | Route nào thắng? Chọn CIDR lab sao cho không trùng? |
| 3 | [Ví dụ: prefix lệch, đường về sai](./docs/03-prefix-fault.md) | 20′ | Vì sao chiều đi đúng mà chiều về sai? |
| 4 | [Lab: tự chia mạng](./lab/01-subnet-plan.md) | 60′ | Tính tay rồi để kernel xác nhận |

## Đạt domain khi bạn có thể

- [ ] Tính tay đúng ≥ 9/10 bài network/broadcast/host range (yêu cầu G-Network: "10 calculations").
- [ ] Dự đoán output `ip route get` (có/không `via`) trước khi chạy.
- [ ] Áp longest prefix match trên route table có ≥ 4 route.
- [ ] Viết address plan có cả đường về, đã kiểm không overlap với route hiện có.

## Liên kết

- Trước: [N02 ARP & ND](../domain02-ARPNeighborDiscovery/README.md)
- Tiếp theo: [N04 Namespace, veth, bridge & VLAN](../domain04-NetnsVethBridgeVLAN/README.md)

## Nguồn

[RFC 4632 CIDR](https://www.rfc-editor.org/rfc/rfc4632) · [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918) · [LPIC-1 109.1](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
