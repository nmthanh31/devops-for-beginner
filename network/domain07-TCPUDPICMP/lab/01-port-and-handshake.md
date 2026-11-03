# N07 Lab — Bind, handshake, refused

| | |
|---|---|
| **Thời lượng** | 60 phút |
| **Môi trường** | VM lab, 2 namespace nối trực tiếp, `python3`, `tcpdump`, `curl` |
| **Mục tiêu** | Thấy tận mắt: bind loopback → refused; bind đúng → handshake; service tắt → RST |

```text
n07-c 10.67.0.10/24 ═══ veth ═══ n07-s 10.67.0.20/24 (HTTP :18087)
```

## Bước 0 — Dựng

```bash
for ns in n07-c n07-s; do sudo ip netns add $ns; sudo ip -n $ns link set lo up; done
sudo ip link add c-e netns n07-c type veth peer name s-e netns n07-s
sudo ip -n n07-c addr add 10.67.0.10/24 dev c-e && sudo ip -n n07-c link set c-e up
sudo ip -n n07-s addr add 10.67.0.20/24 dev s-e && sudo ip -n n07-s link set s-e up
```

## Bước 1 — Bind loopback

```bash
sudo ip netns exec n07-s python3 -m http.server 18087 --bind 127.0.0.1 &
sudo ip netns exec n07-s ss -lntp | grep 18087
sudo ip netns exec n07-s curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18087/
```

**Dự đoán:** client `10.67.0.10` gọi `10.67.0.20:18087` sẽ ra gì? Capture sẽ thấy cờ gì?

```bash
sudo ip netns exec n07-s tcpdump -ni s-e 'tcp port 18087' &      # terminal riêng nếu muốn
sudo ip netns exec n07-c curl -m 3 http://10.67.0.20:18087/
```

**Kết quả mong đợi:** `Connection refused`; capture `[S]` rồi `[R.]`.

## Bước 2 — Bind đúng IP

```bash
sudo pkill -f 'http.server 18087'
sudo ip netns exec n07-s python3 -m http.server 18087 --bind 10.67.0.20 &
sudo ip netns exec n07-c curl -s -o /dev/null -w '%{http_code}\n' http://10.67.0.20:18087/
```

**Kết quả mong đợi:** `200`; capture có `[S]`, `[S.]`, `[.]`, `[P.]` (request/response), `[F.]`. Đánh dấu 3 gói handshake trong evidence.

## Bước 3 — Tắt service

```bash
sudo pkill -f 'http.server 18087'
sudo ip netns exec n07-c curl -m 3 http://10.67.0.20:18087/
```

**Kết quả mong đợi:** lại `refused` + RST. Ghi chú: ở [N09](../../domain09-FirewallConntrackNAT/README.md) bạn sẽ dùng firewall `drop` để tạo **timeout** và so sánh.

## Bước 4 (thêm) — UDP và ICMP Port Unreachable

```bash
sudo ip netns exec n07-s tcpdump -ni s-e 'udp or icmp' &
sudo ip netns exec n07-c bash -c 'echo hi > /dev/udp/10.67.0.20/9999'
```

**Kết quả mong đợi:** UDP datagram tới, server trả `ICMP ... udp port 9999 unreachable`. Lệnh gửi ở client vẫn "thành công" — UDP không biết đích không nghe.

---

## Definition of Done

- [ ] Dự đoán trước mỗi bước.
- [ ] Evidence 2 lớp mỗi bước: `ss` (socket) + `tcpdump` (packet).
- [ ] Bảng so sánh: bind loopback / bind đúng / service tắt / UDP không socket.
- [ ] Giải thích được vì sao refused là RST chứ không phải timeout.

## Cleanup

```bash
sudo pkill -f 'http.server 18087'; sudo pkill -f 'tcpdump -ni s-e'
for ns in n07-c n07-s; do sudo ip netns del $ns; done
ip netns list
```
