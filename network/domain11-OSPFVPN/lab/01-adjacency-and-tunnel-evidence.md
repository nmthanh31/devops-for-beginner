# N11 Lab — Tunnel evidence (WireGuard) và adjacency (OSPF)

| | |
|---|---|
| **Thời lượng** | 2 × 60 phút (hai phần độc lập) |
| **Môi trường** | Phần A: VM lab có `wireguard-tools` (kernel module sẵn trên Ubuntu ≥ 20.04). Phần B: Docker hoặc 2–3 VM có FRR |
| **Mục tiêu** | Chứng minh "control plane xanh ≠ data plane OK" ở cả WireGuard và OSPF |

> Chưa cài được tool? Vẽ topology + dự đoán output trước; không cài package vào VM dùng chung chỉ để hoàn thành lý thuyết.

---

## Phần A — WireGuard giữa hai namespace

```text
n11-a                                   n11-b
 wg0 10.90.0.1/24  ═══ tunnel ═══  wg0 10.90.0.2/24
 u-a 192.0.2.1/24 ─── underlay veth ─── u-b 192.0.2.2/24
```

```bash
for ns in n11-a n11-b; do sudo ip netns add $ns; sudo ip -n $ns link set lo up; done
sudo ip link add u-a netns n11-a type veth peer name u-b netns n11-b
sudo ip -n n11-a addr add 192.0.2.1/24 dev u-a && sudo ip -n n11-a link set u-a up
sudo ip -n n11-b addr add 192.0.2.2/24 dev u-b && sudo ip -n n11-b link set u-b up

mkdir -p ~/n11 && cd ~/n11 && umask 077
for x in a b; do wg genkey | tee $x.key | wg pubkey > $x.pub; done

for x in a b; do
  sudo ip -n n11-$x link add wg0 type wireguard
done
sudo ip netns exec n11-a wg set wg0 private-key a.key listen-port 51820 \
  peer $(cat b.pub) endpoint 192.0.2.2:51820 allowed-ips 10.90.0.2/32
sudo ip netns exec n11-b wg set wg0 private-key b.key listen-port 51820 \
  peer $(cat a.pub) endpoint 192.0.2.1:51820 allowed-ips 10.90.0.1/32
sudo ip -n n11-a addr add 10.90.0.1/24 dev wg0 && sudo ip -n n11-a link set wg0 up
sudo ip -n n11-b addr add 10.90.0.2/24 dev wg0 && sudo ip -n n11-b link set wg0 up
```

> Interface WireGuard tạo trong namespace sẽ dùng socket UDP của namespace đó — underlay là veth `u-a/u-b`.

### A1 — Positive + hai lớp capture

```bash
sudo ip netns exec n11-b tcpdump -ni u-b udp port 51820 -c 4 &
sudo ip netns exec n11-b tcpdump -ni wg0 icmp -c 4 &
sudo ip netns exec n11-a ping -c 2 10.90.0.2
sudo ip netns exec n11-a wg show
```

Ghi: underlay thấy gì (UDP, không đọc được nội dung), `wg0` thấy gì (ICMP inner).

### A2 — Negative: AllowedIPs sai

**Dự đoán** trước: đổi AllowedIPs ở B thành `10.99.0.1/32`. Handshake còn? Ping?

```bash
sudo ip netns exec n11-b wg set wg0 peer $(cat a.pub) allowed-ips 10.99.0.1/32
sudo ip netns exec n11-a ping -c 2 -W 1 10.90.0.2
sudo ip netns exec n11-a wg show | grep -E 'handshake|transfer'
sudo ip netns exec n11-b wg show | grep -E 'handshake|transfer'
```

**Kết quả mong đợi:** handshake vẫn cập nhật; ping fail; B **received** tăng nhưng không trả lời (inner source `10.90.0.1` không thuộc AllowedIPs → drop).

Khôi phục: `sudo ip netns exec n11-b wg set wg0 peer $(cat a.pub) allowed-ips 10.90.0.1/32` → ping lại.

### A3 — Negative: underlay hỏng

`sudo ip -n n11-b link set u-b down` → `wg show` handshake ngừng cập nhật (sau ~2 phút mới "cũ"). Bật lại.

---

## Phần B — OSPF với FRR (Docker)

```text
 lan1 10.11.1.0/24 ── R1 ──10.11.0.0/30── R2 ── lan2 10.11.2.0/24
```

Gợi ý môi trường: hai container `quay.io/frrouting/frr:9.1.0` (privileged) cùng một Docker network `10.11.0.0/29`, mỗi container thêm một dummy interface làm LAN. Bật `ospfd=yes` trong `/etc/frr/daemons`.

Cấu hình R1 (`vtysh`):

```text
configure terminal
 router ospf
  ospf router-id 1.1.1.1
  network 10.11.0.0/29 area 0
  network 10.11.1.0/24 area 0
```

R2 tương tự (`2.2.2.2`, `10.11.2.0/24`).

### Thu evidence theo chuỗi

| Lệnh | Ghi lại |
|---|---|
| `tcpdump -ni eth0 proto ospf -c 4` | Hello hai chiều |
| `show ip ospf neighbor` | Full |
| `show ip ospf database` | LSA của 2 LAN |
| `show ip route ospf` | Route học được |
| `ip route` (trong container) | Route `proto ospf` trong kernel |
| ping LAN↔LAN | Data plane |

### Fault: area mismatch

**Dự đoán** trước. Trên R2 đổi `network 10.11.0.0/29 area 1`. Quan sát neighbor (biến mất), route (mất), log FRR. Sửa về `area 0`, verify route + ping.

Fault thêm (tùy chọn): MTU mismatch (`ip link set eth0 mtu 1400` trên R2) → kẹt `ExStart`.

---

## Definition of Done

- [ ] Sơ đồ ghi rõ outer endpoint IP:port và inner IP.
- [ ] A1: capture underlay vs `wg0` cạnh nhau.
- [ ] A2: chứng minh handshake OK + inner fail, giải thích AllowedIPs.
- [ ] B: chuỗi Hello → Full → LSDB → FRR route → kernel route → ping.
- [ ] B fault: dự đoán, evidence, sửa, verify.

## Cleanup

```bash
for ns in n11-a n11-b; do sudo ip netns del $ns; done
rm -r ~/n11
docker rm -f r1 r2 2>/dev/null; docker network rm n11 2>/dev/null
```
