# N02 Lab — Chứng minh ai được ARP hỏi

| | |
|---|---|
| **Thời lượng** | 60 phút |
| **Môi trường** | VM lab; topology namespace riêng (dựng ở bước 0). Không động vào interface SSH |
| **Mục tiêu** | (1) chứng minh ARP hỏi **next hop** chứ không phải đích cuối; (2) tạo lỗi prefix khiến ARP `FAILED`, rồi khôi phục |

---

## Bước 0 — Dựng topology nhỏ

```text
 n02-a (10.62.1.10/24) ──┐                       ┌── n02-b (10.62.2.20/24)
                         br-n02a ── n02-r ── br-n02b
             gw 10.62.1.1 (r-a)         (r-b) gw 10.62.2.1
```

Kiểm tên chưa tồn tại: `ip netns list; ip -br link | grep n02`. Sau đó:

```bash
for ns in n02-a n02-r n02-b; do sudo ip netns add $ns; sudo ip -n $ns link set lo up; done

# A <-> R
sudo ip link add n02-a-e netns n02-a type veth peer name n02-ra netns n02-r
# R <-> B
sudo ip link add n02-b-e netns n02-b type veth peer name n02-rb netns n02-r

sudo ip -n n02-a addr add 10.62.1.10/24 dev n02-a-e
sudo ip -n n02-r addr add 10.62.1.1/24  dev n02-ra
sudo ip -n n02-r addr add 10.62.2.1/24  dev n02-rb
sudo ip -n n02-b addr add 10.62.2.20/24 dev n02-b-e
for p in "n02-a n02-a-e" "n02-r n02-ra" "n02-r n02-rb" "n02-b n02-b-e"; do set -- $p; sudo ip -n $1 link set $2 up; done

sudo ip -n n02-a route add default via 10.62.1.1
sudo ip -n n02-b route add default via 10.62.2.1
sudo ip netns exec n02-r sysctl -qw net.ipv4.ip_forward=1
```

> Ở đây dùng veth nối thẳng (không cần bridge) cho gọn. Router chỉ là một namespace bật `ip_forward`.

Kiểm nhanh: `sudo ip netns exec n02-a ping -c1 10.62.2.20` phải thành công.

## Bước 1 — Dự đoán

Điền **trước** khi chạy:

| Đích từ A | Có `via`? | ARP sẽ hỏi IP nào? |
|---|---|---|
| `10.62.1.1` (cùng subnet) | | |
| `10.62.2.20` (khác subnet) | | |

## Bước 2 — Quan sát

Terminal 1:

```bash
sudo ip -n n02-a neigh flush all
sudo ip netns exec n02-a tcpdump -eni n02-a-e 'arp or icmp'
```

Terminal 2:

```bash
sudo ip -n n02-a route get 10.62.2.20
sudo ip netns exec n02-a ping -c 2 10.62.2.20
sudo ip -n n02-a neigh
```

**Kết quả mong đợi:** chỉ thấy `who-has 10.62.1.1` — **không** có `who-has 10.62.2.20`. ICMP đi trong frame tới MAC của `n02-ra`. `ip neigh` chỉ có entry `10.62.1.1`.

## Bước 3 — Negative test: prefix sai

Đổi prefix A thành `/16` (chỉ trong namespace lab):

```bash
sudo ip -n n02-a addr del 10.62.1.10/24 dev n02-a-e
sudo ip -n n02-a addr add 10.62.1.10/16 dev n02-a-e
sudo ip -n n02-a route add default via 10.62.1.1   # route default bị xóa theo address, thêm lại
sudo ip -n n02-a route get 10.62.2.20
sudo ip netns exec n02-a ping -c 2 -W 1 10.62.2.20
sudo ip -n n02-a neigh show 10.62.2.20
```

**Dự đoán rồi kiểm:** `route get` giờ **không** còn `via` (on-link vì `/16`). Capture thấy `who-has 10.62.2.20` lặp lại không reply; neighbor → `FAILED`. Ping fail.

Viết 3 dòng: vì sao B không nhận được ARP?

## Bước 4 — Khôi phục và positive test

```bash
sudo ip -n n02-a addr del 10.62.1.10/16 dev n02-a-e
sudo ip -n n02-a addr add 10.62.1.10/24 dev n02-a-e
sudo ip -n n02-a route replace default via 10.62.1.1
sudo ip netns exec n02-a ping -c 2 10.62.2.20
```

---

## Definition of Done

- [ ] Bảng dự đoán điền trước, đánh dấu đúng/sai.
- [ ] Capture bước 2 chứng minh ARP hỏi gateway, không hỏi đích cuối.
- [ ] Bước 3 có đủ **hai lớp evidence**: `route get` (không `via`) + capture/neigh `FAILED`.
- [ ] Giải thích causal: prefix `/16` → on-link → ARP trực tiếp → B khác link → không reply.
- [ ] Positive test sau khi khôi phục.

## Cleanup

```bash
for ns in n02-a n02-r n02-b; do sudo ip netns pids $ns; done   # phải rỗng
for ns in n02-a n02-r n02-b; do sudo ip netns del $ns; done
ip netns list; ip -br link | grep n02 || echo "sạch"
```

Veth nằm trong namespace nên tự biến mất khi xóa namespace.
