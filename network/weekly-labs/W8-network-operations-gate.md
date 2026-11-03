# W8 Lab chính — Network operations gate

| | |
|---|---|
| **Thời lượng** | Build ~4h + gate 10 incident |
| **Cần trước** | [N09](../domain09-FirewallConntrackNAT/README.md)–[N12](../domain12-CloudK8sNetwork/README.md) và các lab domain tương ứng |
| **Gate G-Network** | 10 incident phủ ≥ 9/12 domain; root cause ≥ 8, fix/rollback ≥ 7; luôn giải thích chiều đi–về |

> **Mẹo:** tái dùng script dựng topology từ lab [N05](../domain05-RoutingReturnPath/lab/01-two-way-route.md), [N09](../domain09-FirewallConntrackNAT/lab/01-isolated-filter-nat.md), [N10](../domain10-LossMTU/lab/01-netem-and-mtu.md), [N11](../domain11-OSPFVPN/lab/01-adjacency-and-tunnel-evidence.md), [N12](../domain12-CloudK8sNetwork/lab/01-service-path-evidence.md). Lưu chúng thành `setup.sh`/`cleanup.sh` để reset baseline nhanh giữa các incident.

## Mục tiêu

Chẩn đoán 10 incident trên topology nhiều hop. Chỉ thay đổi tài nguyên lab; mọi thay đổi firewall/qdisc/tunnel có baseline và rollback.

```text
client → router/firewall/NAT → tunnel hoặc overlay → service
                                     ├→ Kubernetes Service → EndpointSlice → pod
                                     └→ HAProxy frontend → backend A/B
```

## Bốn nhánh cần chứng minh

1. **Firewall/conntrack/NAT:** ruleset, hook/chain, connection state, packet trước và sau dịch IP.
2. **Loss/MTU:** baseline RTT, packet loss, retransmission, Path MTU và ICMP Packet Too Big/fragmentation needed nếu có.
3. **OSPF/VPN:** neighbor/adjacency, route được cài, outer endpoint route, tunnel handshake và inner traffic.
4. **Cloud/Kubernetes:** subnet route/security layer, Service selector, EndpointSlice, pod readiness, NetworkPolicy và application listener.
5. **HAProxy vận hành:** `global`/`defaults`/`frontend`/`backend`, `mode tcp` so với `mode http`, Host/path ACL, `roundrobin` so với `leastconn`, active `/healthz`, timeout và stats/log.

Ở nhánh HAProxy, dùng hai backend lab có response phân biệt. Chứng minh cả hai được chọn khi khỏe; dừng một backend rồi đợi health check đánh dấu down và chứng minh traffic mới vẫn thành công qua backend còn lại. Cố ý sửa sai health path, ACL hoặc timeout **từng lỗi một**; ghi lỗi nào tạo 503, lỗi nào đưa request vào backend sai, và lỗi nào chỉ làm request chậm. So sánh với Nginx TLS/proxy ở W7 để hiểu ranh giới giữa hai sản phẩm.

## Incident matrix đề xuất

Bảng có 12 lựa chọn. Chọn **10 incident phủ ít nhất 9 domain**, trong đó có N09–N12; giữ một incident HAProxy để luyện phần load balancer của W8. Mỗi fault tạo trong lab riêng, trả baseline rồi mới chuyển sang fault tiếp theo.

| Domain | Fault | Evidence tối thiểu |
|---|---|---|
| N01 | Capture sai interface làm đọc nhầm packet journey | capture point + MAC/IP/port đúng |
| N02 | Neighbor `FAILED` vì gateway ở sai VLAN | route get + ARP/ND capture |
| N03 | Prefix sai khiến host coi remote là on-link | tính CIDR + route get + neighbor |
| N04 | VLAN membership lệch | bridge VLAN/FDB + capture hai port |
| N05 | Thiếu return route | route get hai đầu + paired capture |
| N06 | DNS trả IP cũ hoặc sai | dig/getent/TTL + authoritative answer |
| N07 | Listener bind loopback hoặc TCP bị drop | ss + SYN/RST/timeout capture |
| N08 | HAProxy health path/ACL sai | config check + stats/log + response backend |
| N09 | SNAT/conntrack/rule order sai | nft ruleset/counter + tuple trước/sau NAT |
| N10 | MTU/PMTUD black hole hoặc netem loss | size threshold/RTT + paired capture |
| N11 | OSPF adjacency hoặc WireGuard inner route sai | neighbor/route hoặc `wg show` + route get |
| N12 | Service thiếu EndpointSlice hoặc NetworkPolicy chặn | Service/pods/EndpointSlice/policy + client test |

Với N09–N12, thực hiện đủ bốn nhánh ở trên. Với các domain cũ hơn, chọn các hàng còn lại sao cho tổng đúng 10 incident và ít nhất 9 domain. Mỗi incident chỉ được tính khi có test sau sửa và rollback.

Nếu chưa có FRR, WireGuard hoặc Kubernetes lab, không ghi nhánh đó là đã PASS; có thể làm phần phân tích trên output mẫu rồi hoàn thiện lab khi môi trường sẵn sàng.

## Cách chấm

Với mỗi incident: viết hypothesis trước lệnh, thu ít nhất hai lớp evidence, xác định root cause, sửa tối thiểu, positive + negative verify và rollback. Gate Calendar yêu cầu xác định đúng ít nhất 8/10 và sửa ít nhất 7/10. Không tính điểm chỉ vì chạy nhiều lệnh.

### Mẫu scorecard

| # | Domain | Triệu chứng | Hypothesis | Evidence 1 | Evidence 2 | Chiều đi / về | Root cause | Fix | Verify +/− | Rollback | Đúng? | Sửa? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | | | |

Tổng: domain phủ __/12 · đúng __/10 · sửa __/10.

Nguồn: [nftables](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes), [tc-netem](https://man7.org/linux/man-pages/man8/tc-netem.8.html), [FRR OSPF](https://docs.frrouting.org/en/latest/ospfd.html), [Kubernetes Service](https://kubernetes.io/docs/concepts/services-networking/service/), [HAProxy configuration manual](https://docs.haproxy.org/3.2/configuration.html).
