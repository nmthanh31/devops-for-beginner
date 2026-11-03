# N05 Bài 1 — Route đi và route về

> **Sau bài này bạn sẽ:**
> - Hiểu route đi (ở client) và route về (ở server) là **hai quyết định độc lập** trên hai máy.
> - Ghi đủ 4 thông tin khi debug route: destination, route được chọn, egress interface, source IP.
> - Biết router Linux cần gì để forward: route + `ip_forward` + firewall `FORWARD`.
>
> **Cần trước:** [N03 — longest prefix match](../../domain03-CIDRSubnetting/docs/02-address-plan-and-overlap.md).

---

## 1. Hình dung: đường một chiều

Bạn gửi thư cho bạn ở thành phố khác. Bưu điện của bạn biết đường đi (route đi). Nhưng thư hồi âm do **bưu điện bên kia** quyết định đường — nếu họ không biết đường về thành phố bạn, thư hồi âm thất lạc, dù thư đi đã tới nơi.

```text
Client A (10.51.1.10) ──► Router ──► Server B (10.52.1.20)
                           ◄── ?? ◄──
Client cần route tới 10.52.1.0/24      ← quyết định trên A
Server cần route tới 10.51.1.0/24      ← quyết định trên B (độc lập!)
```

Thiếu route về: A thấy **timeout**, dù B **đã nhận** SYN/Echo Request. Gói phản hồi có source/destination **đảo ngược** so với request.

## 2. Một route gồm gì

Route = quy tắc *"đích thuộc prefix này → gửi qua interface nào, có cần gateway nào"*.

| Thành phần | Ý nghĩa | Ví dụ |
|---|---|---|
| Destination prefix | Đích nào khớp | `10.52.1.0/24` |
| Gateway / next hop | Router kế tiếp chạm được trực tiếp trên link | `via 10.51.1.1` |
| Interface | Cổng ra | `dev veth-a` |
| Source IP | Địa chỉ đặt vào packet | `src 10.51.1.10` |

**Các loại route:**

- **Connected route**: tự sinh khi gán IP/prefix lên interface (`proto kernel scope link`).
- **Static route**: bạn thêm bằng tay.
- **Default route** `0.0.0.0/0`: dùng khi không có prefix nào cụ thể hơn.

## 3. Kernel chọn route thế nào

1. **Longest prefix match** — prefix dài nhất khớp thắng.
2. Trong các route cùng độ dài: **metric** thấp hơn thắng.
3. **Policy routing** (`ip rule`) có thể chọn bảng route khác *trước cả hai bước trên* (Bài 2).

```text
10.52.0.0/16 via 10.51.1.1
10.52.1.0/24 via 10.51.1.2
Đích 10.52.1.20 → /24 thắng → via 10.51.1.2
```

> "Default gateway đúng" **không** chứng minh route đúng — có thể có route cụ thể hơn trỏ nhầm.

```bash
ip route                     # xem bảng
ip route get 10.52.1.20      # kernel SẼ dùng gì cho đích này
```

Chạy `ip route get` ở **cả hai đầu**.

---

## 4. Router Linux: ba điều kiện

```text
packet vào interface A
  → đích không phải IP local của router?
  → ① net.ipv4.ip_forward = 1 ?        (không → drop)
  → ② firewall chain FORWARD cho qua?  (không → drop)
  → ③ tra route → interface B, next hop
  → giảm TTL, đóng frame mới, gửi ra B
```

| Điều kiện | Kiểm | Lưu ý |
|---|---|---|
| Forwarding bật | `sysctl net.ipv4.ip_forward` | Mỗi namespace có giá trị **riêng** |
| Firewall FORWARD | `nft list ruleset` | `ip_forward=1` vẫn có thể bị chặn |
| Route ở router | `ip route` | Cần route tới **cả hai phía** (connected thường đủ) |

---

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Client ping fail → lỗi ở client." | Có thể server thiếu route về. |
| "Server nhận SYN là route ổn." | Mới chứng minh chiều đi. |
| "Bật `ip_forward` là router chạy." | Còn route và firewall FORWARD. |
| "Route thêm sau thắng." | Longest prefix → metric → policy. |

## Tự kiểm tra

1. Capture trên server thấy Echo Request đến và Echo Reply đi ra, client không nhận reply. Hai nguyên nhân có thể?
2. Bảng có `default via .1 metric 100` và `default via .2 metric 50`. Kernel chọn gì?
3. Namespace router có route đầy đủ nhưng không forward. Kiểm hai thứ gì?

<details>
<summary>Đáp án</summary>

1. Server route reply qua next hop sai (route về sai/thiếu), hoặc thiết bị trên đường về (router/firewall) drop.
2. `via .2` (metric thấp hơn).
3. `sysctl net.ipv4.ip_forward` **trong namespace router**, và firewall chain FORWARD.

</details>

## Nguồn

- [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html)
- [LPIC-1 109.3](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
