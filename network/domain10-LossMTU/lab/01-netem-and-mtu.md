# N10 Lab — Netem và MTU trong veth lab

| | |
|---|---|
| **Thời lượng** | 90 phút |
| **Môi trường** | VM lab, `tc` (iproute2), `tcpdump`, `tracepath`, `python3`, `curl` |
| **Mục tiêu** | (1) tạo delay/loss, thấy retransmission, chứng minh nhân quả; (2) tìm ngưỡng MTU, phân biệt chặn tại source vs tại router |
| **An toàn** | **Không** áp `tc`/`mtu` lên `ens33` hoặc NIC quản trị |

## Phần 1 — Delay & loss

```text
n10-a 10.70.0.1/24 ═══ veth ═══ n10-b 10.70.0.2/24
```

```bash
for ns in n10-a n10-b; do sudo ip netns add $ns; sudo ip -n $ns link set lo up; done
sudo ip link add a-e netns n10-a type veth peer name b-e netns n10-b
sudo ip -n n10-a addr add 10.70.0.1/24 dev a-e && sudo ip -n n10-a link set a-e up
sudo ip -n n10-b addr add 10.70.0.2/24 dev b-e && sudo ip -n n10-b link set b-e up
sudo ip netns exec n10-b bash -c 'head -c 5M /dev/urandom > /tmp/n10.bin; cd /tmp && python3 -m http.server 8000 --bind 10.70.0.2 >/dev/null 2>&1 &'
```

**Baseline:**

```bash
sudo ip netns exec n10-a ping -c 20 -q 10.70.0.2
sudo ip netns exec n10-a curl -s -o /dev/null -w 'total=%{time_total}\n' http://10.70.0.2:8000/n10.bin
```

**Dự đoán** (viết ra): thêm `delay 80ms loss 5%` trên egress của **b-e** → ping RTT và % loss thay đổi thế nào? Thời gian tải?

```bash
sudo ip netns exec n10-b tc qdisc add dev b-e root netem delay 80ms loss 5%
sudo ip netns exec n10-a ping -c 20 -q 10.70.0.2
sudo ip netns exec n10-a tcpdump -ni a-e -w /tmp/n10-loss.pcap 'tcp port 8000' &
sudo ip netns exec n10-a curl -s -o /dev/null -w 'total=%{time_total}\n' http://10.70.0.2:8000/n10.bin
sudo pkill -f n10-loss.pcap
tcpdump -nr /tmp/n10-loss.pcap 2>/dev/null | wc -l
```

Mở pcap bằng Wireshark (filter `tcp.analysis.retransmission`) hoặc đếm seq lặp. Sau đó **xóa qdisc và đo lại**:

```bash
sudo ip netns exec n10-b tc qdisc del dev b-e root
sudo ip netns exec n10-a ping -c 20 -q 10.70.0.2
```

| | RTT avg | Loss | Tải 5MB | Retransmit |
|---|---|---|---|---|
| Baseline | | | | |
| netem | | | | |
| Sau khi xóa | | | | |

## Phần 2 — MTU qua router

```text
n10-a ═══ (MTU 1500) ═══ n10-r ═══ (MTU 1400) ═══ n10-c
10.71.1.10           .1  router  .1          10.71.2.10
```

```bash
sudo ip netns add n10-r; sudo ip netns add n10-c
for ns in n10-r n10-c; do sudo ip -n $ns link set lo up; done
sudo ip link add a2 netns n10-a type veth peer name r1 netns n10-r
sudo ip link add c2 netns n10-c type veth peer name r2 netns n10-r
sudo ip -n n10-a addr add 10.71.1.10/24 dev a2; sudo ip -n n10-r addr add 10.71.1.1/24 dev r1
sudo ip -n n10-r addr add 10.71.2.1/24 dev r2;  sudo ip -n n10-c addr add 10.71.2.10/24 dev c2
for p in "n10-a a2" "n10-r r1" "n10-r r2" "n10-c c2"; do set -- $p; sudo ip -n $1 link set $2 up; done
sudo ip -n n10-a route add 10.71.2.0/24 via 10.71.1.1
sudo ip -n n10-c route add 10.71.1.0/24 via 10.71.2.1
sudo ip netns exec n10-r sysctl -qw net.ipv4.ip_forward=1
sudo ip -n n10-r link set r2 mtu 1400; sudo ip -n n10-c link set c2 mtu 1400
```

**Dự đoán:** `-s` lớn nhất qua được? Lỗi báo tại đâu khi vượt?

```bash
for s in 1300 1372 1373 1472; do echo "== $s"; sudo ip netns exec n10-a ping -M do -c 1 -W 1 -s $s 10.71.2.10 | tail -2; done
sudo ip netns exec n10-a tracepath -n 10.71.2.10
sudo ip -n n10-a route get 10.71.2.10      # có "cache expires ... mtu 1400" sau khi học PMTU
```

**Kết quả mong đợi:** `1372` OK; `1373` nhận `Frag needed and DF set (mtu = 1400)` **từ 10.71.1.1** lần đầu, các lần sau báo `message too long` **ngay tại source** (đã cache PMTU). `tracepath` báo `pmtu 1400`.

**Thí nghiệm black hole:** chặn ICMP trên router rồi thử lại sau khi xóa cache:

```bash
sudo ip netns exec n10-r nft add table ip n10; sudo ip netns exec n10-r nft add chain ip n10 out '{ type filter hook output priority 0; }'
sudo ip netns exec n10-r nft add rule ip n10 out icmp type destination-unreachable drop
sudo ip -n n10-a route flush cache
sudo ip netns exec n10-a ping -M do -c 2 -W 1 -s 1373 10.71.2.10    # timeout im lặng
sudo ip netns exec n10-r nft delete table ip n10
```

---

## Definition of Done

- [ ] Bảng phần 1 đủ 3 hàng; chứng minh nhân quả bằng "xóa qdisc → hết".
- [ ] Chỉ ra ≥ 1 retransmission trong pcap.
- [ ] Ngưỡng `-s` đúng = MTU − 28, giải thích phép tính.
- [ ] Phân biệt lỗi tại source vs ICMP từ router.
- [ ] Black hole: timeout im lặng khi ICMP bị chặn.

## Cleanup

```bash
sudo pkill -f 'http.server 8000'
for ns in n10-a n10-b n10-r n10-c; do sudo ip netns del $ns; done
rm -f /tmp/n10-loss.pcap; ip netns list
```
