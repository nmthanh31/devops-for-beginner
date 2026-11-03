# N04 Lab — Tự dựng topology cô lập

| | |
|---|---|
| **Thời lượng** | 60–75 phút |
| **Môi trường** | VM lab, `iproute2`, `bridge`, `tcpdump`, `sudo` |
| **Mục tiêu** | Dựng 2 namespace + bridge từ blank, nối được MAC ↔ ARP ↔ ICMP ↔ FDB, rồi break/fix một port |
| **An toàn** | Chỉ tạo tài nguyên tên `n04-*`/`br-n04`. **Không** gắn NIC vật lý/SSH vào bridge |

```text
 n04-a (10.64.1.11/24)            n04-b (10.64.1.12/24)
   n04-a-e                          n04-b-e
     ║ veth                           ║ veth
   n04-a-h ─────── br-n04 ─────── n04-b-h
```

## Bước 0 — Kiểm tên chưa tồn tại

```bash
ip netns list
ip -br link | grep -E 'n04|br-n04' || echo "chưa có — OK"
```

Nếu đã có, **dừng lại** xem đó là gì; không xóa bừa.

## Bước 1 — Tự làm (20 phút, không nhìn gợi ý)

1. Tạo namespace `n04-a`, `n04-b`, hai veth pair, bridge `br-n04`.
2. Một đầu mỗi pair vào namespace; đầu còn lại làm port của bridge.
3. Gán `10.64.1.11/24`, `10.64.1.12/24`; bật `lo`, các veth, bridge.
4. Ping `n04-a → n04-b` thành công.

<details>
<summary>Gợi ý lệnh (mở nếu bí sau 20 phút)</summary>

```bash
sudo ip link add br-n04 type bridge && sudo ip link set br-n04 up
for x in a b; do
  sudo ip netns add n04-$x
  sudo ip link add n04-$x-h type veth peer name n04-$x-e
  sudo ip link set n04-$x-e netns n04-$x
  sudo ip link set n04-$x-h master br-n04
  sudo ip link set n04-$x-h up
  sudo ip -n n04-$x link set lo up
  sudo ip -n n04-$x link set n04-$x-e up
done
sudo ip -n n04-a addr add 10.64.1.11/24 dev n04-a-e
sudo ip -n n04-b addr add 10.64.1.12/24 dev n04-b-e
sudo ip netns exec n04-a ping -c 2 10.64.1.12
```

</details>

## Bước 2 — Nối các bảng với capture

Terminal 1:

```bash
sudo tcpdump -eni br-n04 'arp or icmp'
```

Terminal 2:

```bash
sudo ip -n n04-a neigh flush all
sudo ip netns exec n04-a ping -c 2 10.64.1.12
ip -n n04-a link show n04-a-e | grep ether     # MAC của A
ip -n n04-b link show n04-b-e | grep ether     # MAC của B
sudo ip -n n04-a neigh                          # IP → MAC
bridge fdb show br br-n04 | grep -v permanent   # MAC → port
```

Điền bảng:

| | MAC | Thấy trong capture ở dòng nào? | FDB: port nào? |
|---|---|---|---|
| A (`10.64.1.11`) | | | |
| B (`10.64.1.12`) | | | |

## Bước 3 — Break/fix một port

**Dự đoán trước** (viết ra): tắt `n04-b-h` thì ping, `ip neigh` của A và FDB thay đổi thế nào?

```bash
sudo ip link set n04-b-h down
sudo ip netns exec n04-a ping -c 3 -W 1 10.64.1.12
sudo ip -n n04-a neigh show 10.64.1.12
bridge link | grep n04
```

**Kết quả mong đợi:** ping fail; `bridge link` cho thấy `n04-b-h` `state disabled`/`DOWN`; neighbor dần thành `FAILED` (có thể vẫn `STALE`/`REACHABLE` vài giây đầu do cache — ghi lại thời điểm).

Khôi phục và verify:

```bash
sudo ip link set n04-b-h up
sudo ip netns exec n04-a ping -c 2 10.64.1.12
```

> VLAN để dành cho [W6 lab tích hợp](../../weekly-labs/W6-l2-l3-foundation.md).

---

## Definition of Done

- [ ] Dựng xong từ blank; ghi lại mình có mở gợi ý không.
- [ ] Bảng MAC/capture/FDB đầy đủ, giải thích được vì sao FDB là `MAC → port` còn neigh là `IP → MAC`.
- [ ] Break/fix: dự đoán viết trước, evidence ≥ 2 lớp (`bridge link` + ping/neigh), positive test sau khi sửa.
- [ ] Cleanup sạch.

## Cleanup

```bash
sudo ip netns pids n04-a; sudo ip netns pids n04-b    # phải rỗng
sudo ip netns del n04-a
sudo ip netns del n04-b
sudo ip link del br-n04
ip netns list; ip -br link | grep -E 'n04|br-n04' || echo "sạch"
```

Xóa đúng tên, không dùng wildcard. Veth biến mất cùng namespace.
