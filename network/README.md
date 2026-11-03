# Network N01–N12

12 domain, học trong 3 tuần (W6–W8). Mỗi domain đều trả lời một câu hỏi trên **hành trình của một request**; domain sau dùng lại cơ chế của domain trước.

## Bản đồ: một request đi qua những domain nào

```text
 curl https://app.lab/api
   │
   ├─ Tên → IP?                                N06 DNS
   ├─ IP đích on-link hay qua gateway?          N03 CIDR  →  N05 Routing
   ├─ MAC của next hop?                         N02 ARP/ND
   ├─ Đóng gói frame, đi qua switch/VLAN        N01 Ethernet  →  N04 bridge/VLAN
   ├─ Firewall/NAT trên đường có cho qua?       N09 Firewall/NAT
   ├─ Packet có vừa MTU, có mất gói?            N10 Loss/MTU
   ├─ Đường giữa site/router học từ đâu?        N11 OSPF/VPN
   ├─ TCP handshake tới port                    N07 TCP/UDP/ICMP
   ├─ TLS + HTTP qua reverse proxy/LB           N08 HTTP/TLS/proxy
   └─ Tất cả map lên Docker/K8s/AWS             N12 Cloud/K8s
```

## Lịch học

### W6 — L2/L3 foundation · 02–08/11/2026

| Domain | Câu hỏi chính |
|---|---|
| [N01 Encapsulation & Ethernet](./domain01-EncapsulationEthernet/README.md) | Request được đóng gói thế nào; MAC/IP/port đổi ở đâu? |
| [N02 ARP & Neighbor Discovery](./domain02-ARPNeighborDiscovery/README.md) | Làm sao biết MAC của next hop? |
| [N03 CIDR & subnetting](./domain03-CIDRSubnetting/README.md) | Đích nào on-link, đích nào qua gateway? |
| [N04 Namespace, veth, bridge & VLAN](./domain04-NetnsVethBridgeVLAN/README.md) | Dựng nhiều máy/switch trên một VM, VLAN chia broadcast domain |

Lab tuần: [W6 two VLAN topology](./weekly-labs/W6-l2-l3-foundation.md) · [hướng dẫn từng bước](./weekly-labs/W6-guided-topology.md).

### W7 — Routing đến application · 09–15/11/2026

| Domain | Câu hỏi chính |
|---|---|
| [N05 Routing & return path](./domain05-RoutingReturnPath/README.md) | Packet đi và **về** bằng đường nào? |
| [N06 DHCP, DNS & time](./domain06-DHCPDNSTime/README.md) | Máy nhận IP, phân giải tên, đồng bộ giờ thế nào? |
| [N07 TCP, UDP & ICMP](./domain07-TCPUDPICMP/README.md) | `refused` khác `timeout` ra sao? |
| [N08 HTTP, TLS & reverse proxy](./domain08-HTTPTLSReverseProxy/README.md) | 502/503/cert lỗi nằm ở đoạn nào? |

Lab tuần: [W7 routed HTTPS application](./weekly-labs/W7-routing-to-application.md).

### W8 — Network operations gate · 16–22/11/2026

| Domain | Câu hỏi chính |
|---|---|
| [N09 Firewall, conntrack & NAT](./domain09-FirewallConntrackNAT/README.md) | Rule nào chặn, tuple đổi thế nào qua NAT? |
| [N10 Loss & MTU](./domain10-LossMTU/README.md) | Vì sao gói nhỏ qua, gói lớn treo? |
| [N11 OSPF & VPN](./domain11-OSPFVPN/README.md) | Route động và tunnel hỏng trông ra sao? |
| [N12 Cloud & Kubernetes network path](./domain12-CloudK8sNetwork/README.md) | Map một flow Linux → Docker → K8s → AWS |

Lab tuần: [W8 network operations gate](./weekly-labs/W8-network-operations-gate.md).

## Cách học một domain

Mỗi domain có cùng cấu trúc:

| Phần | Làm gì |
|---|---|
| `README.md` | Đọc câu hỏi chính + "mô hình một câu" + checklist đạt domain |
| `docs/01`, `docs/02` | Cơ chế. Mỗi bài: mục tiêu → hình dung → cơ chế từng bước → hiểu lầm → **tự kiểm tra** (đáp án ẩn) |
| `docs/03` | Ví dụ chẩn đoán. **Dừng ở chỗ ✋ và tự dự đoán** trước khi đọc tiếp |
| `lab/01` | Dự đoán → chạy → so với "kết quả mong đợi" → checklist DoD → cleanup |

Luật PASS (theo roadmap): *prediction → baseline → one change → evidence ≥ 2 lớp → giải thích nhân quả → sửa tối thiểu → positive + negative verify → cleanup.*

## An toàn lab

- Mọi lab thay đổi route/firewall/qdisc chạy trong **namespace hoặc VM lab** có console recovery.
- Đặt tên tài nguyên theo domain (`n04-*`, `br-w6`), kiểm tên chưa tồn tại trước khi tạo, cleanup đúng tên — không dùng wildcard.
- Không gắn NIC quản trị/SSH vào bridge lab; không đổi IP interface đang SSH.
