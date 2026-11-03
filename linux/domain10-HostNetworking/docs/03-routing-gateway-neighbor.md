# Bài 3 — Routing table, gateway và neighbor

## Mục tiêu và tiền đề

Bài này dùng interface, IP và prefix từ Bài 2 để giải thích cách kernel chọn đường cho packet.

Đọc trước: [Interface, địa chỉ IP và CIDR](./02-interfaces-addresses-cidr.md).

## 1. Routing và routing table

**Routing** là quá trình quyết định packet cần đi theo đường nào để tới destination network.

**Routing table** là bảng các route trong kernel. Nó không cần chứa từng host trên Internet; một route prefix có thể đại diện cả dải destination.

```bash
ip route
```

Ví dụ:

```text
default via 192.168.220.2 dev ens33 metric 100
192.168.220.0/24 dev ens33 proto kernel scope link src 192.168.220.133
```

## 2. Một route gồm gì?

**Route** là một entry trong routing table. Các trường thường gặp:

| Trường | Ý nghĩa |
|---|---|
| destination prefix | Dải IP mà route áp dụng |
| `via` | Gateway/next hop |
| `dev` | Interface đầu ra |
| `src` | Source IP ưu tiên |
| `metric` | Độ ưu tiên giữa route tương đương |
| `scope` | Phạm vi của route |
| `proto` | Nguồn tạo route, ví dụ kernel hoặc DHCP |

Route `scope link` cho biết destination reachable trực tiếp trên link. Route `proto kernel` thường được tạo từ address/prefix gắn trên interface.

## 3. Các loại route chính

### Local route

Destination là địa chỉ thuộc chính host. Packet được local-deliver, không cần gửi ra NIC.

### Connected/on-link route

Destination nằm trong subnet trực tiếp. Host tìm MAC của destination và gửi frame trực tiếp.

### Route qua gateway

Destination nằm ở network khác. Host gửi frame cho gateway; gateway route packet tiếp.

### Default route

Route dự phòng ít cụ thể nhất:

```text
IPv4: 0.0.0.0/0
IPv6: ::/0
```

Nó được dùng khi không có route cụ thể hơn.

## 4. Longest-prefix match và metric

Kernel tìm mọi route khớp destination rồi ưu tiên prefix dài nhất:

```text
10.10.20.0/24  cụ thể hơn 10.10.0.0/16
10.10.0.0/16   cụ thể hơn 10.0.0.0/8
default /0      ít cụ thể nhất
```

Metric thường chỉ giúp lựa chọn giữa các route có mức cụ thể tương đương. Metric thấp hơn thường được ưu tiên trong trường hợp thông thường.

## 5. Gateway và next hop

**Gateway** là router trên local subnet có thể chuyển packet sang network khác. **Next hop** là thiết bị kế tiếp trực tiếp nhận frame.

Khi gửi tới remote host:

```text
IP destination  = remote host
MAC destination = gateway hiện tại
```

Host không đổi IP destination thành IP gateway. Gateway chỉ là next hop ở link hiện tại.

## 6. Route lookup và source IP

```bash
ip route get 8.8.8.8
```

Lệnh này yêu cầu kernel cho biết quyết định dự kiến:

- route nào;
- gateway nào;
- interface nào;
- source IP nào.

Nó thường hữu ích hơn chỉ nhìn toàn bảng route khi điều tra một destination cụ thể.

## 7. Neighbor table

Sau khi route chọn next hop, kernel cần địa chỉ link/MAC để tạo frame.

**Neighbor table** là cache ánh xạ neighbor IP → địa chỉ link:

```bash
ip neigh
```

Trạng thái thường gặp:

- `REACHABLE`: vừa được xác nhận reachable;
- `STALE`: entry cũ nhưng chưa phải lỗi, sẽ được kiểm tra lại khi cần;
- `DELAY`/`PROBE`: kernel đang xác nhận;
- `FAILED`: không phân giải/xác nhận được neighbor.

## 8. ARP và IPv6 Neighbor Discovery

Với IPv4 trên Ethernet, ARP hoạt động đơn giản:

1. Kernel cần MAC của một IP on-link.
2. Kernel kiểm tra neighbor cache.
3. Nếu chưa có, host broadcast ARP request.
4. Chủ sở hữu IP trả ARP reply chứa MAC.
5. Kernel lưu mapping và gửi frame.

IPv6 không dùng ARP. Nó dùng **Neighbor Discovery** dựa trên ICMPv6 để tìm neighbor/router và kiểm tra reachability.

## 9. Policy routing

Linux có thể chọn routing table bằng rule dựa trên source IP, packet mark hoặc thuộc tính khác:

```bash
ip rule
ip route show table all
```

Đây là phần nâng cao, thường gặp ở host nhiều NIC, VPN hoặc routing policy. Bảng `main` không phải lúc nào cũng là toàn bộ câu chuyện.

## 10. Runtime route không persistent

```bash
sudo ip route add 198.51.100.0/24 via 192.168.220.2 dev ens33
```

Lệnh này thay đổi runtime. Muốn giữ sau reboot, route phải được khai báo trong hệ thống quản lý mạng.

<!-- learn:tail -->
## Tự kiểm tra

1. `ip route get 8.8.8.8` → `via 192.168.220.2 dev ens33 src 192.168.220.133`. Ba thông tin này dùng để làm gì?
2. Gateway đúng trong route table nhưng `ip neigh` báo `FAILED` cho gateway. Lỗi lớp nào?

<details>
<summary>Đáp án</summary>

1. Next hop để ARP, interface để gửi ra, source IP đặt vào packet.
2. Link/L2 tới gateway (VMware network, VLAN, gateway down) — không phải route ([N02](../../../network/domain02-ARPNeighborDiscovery/README.md)).

</details>

## Nguồn

- [LPIC-1 V5.0 — Objective 109.3](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

