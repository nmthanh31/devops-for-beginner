# N02 Bài 1 — ARP: biến next-hop IP thành MAC

> **Sau bài này bạn sẽ:**
> - Biết **thứ tự**: route lookup chọn next hop *trước*, ARP hỏi MAC của next hop *sau*.
> - Đọc được trạng thái neighbor cache (`REACHABLE`, `STALE`, `INCOMPLETE`, `FAILED`) và biết trạng thái nào **chưa** chứng minh điều gì.
> - Dự đoán IP nào sẽ bị ARP khi đổi prefix.
>
> **Cần trước:** [N01 — các lớp và đóng gói](../../domain01-EncapsulationEthernet/docs/01-layers-and-frames.md).

---

## 1. Hình dung: gọi to trong phòng

Bạn biết tên người cần gửi (IP) nhưng không biết họ ngồi ghế nào (MAC). Bạn đứng giữa phòng gọi to: *"Ai là 10.66.10.1? Bảo cho tôi biết với!"* (broadcast). Đúng người giơ tay trả lời riêng bạn (unicast). Bạn ghi vào sổ tay để lần sau khỏi hỏi lại — đó là **neighbor cache**.

Tiếng gọi chỉ vang **trong phòng** (broadcast domain). Phòng bên cạnh (VLAN/subnet khác) không nghe thấy.

## 2. ARP là gì

**ARP (Address Resolution Protocol)** hỏi: *"Thiết bị nào giữ IPv4 này, MAC của nó là gì?"*. ARP chỉ dùng cho IPv4; IPv6 dùng ND (Bài 2).

## 3. Thứ tự quan trọng nhất: route trước, ARP sau

```text
① Route lookup: đích có on-link không?
      ├─ có  (route "dev X", không "via")  → next hop = chính IP đích
      └─ không (route "via GW dev X")      → next hop = IP gateway
② ARP hỏi MAC của NEXT HOP (không phải của đích cuối)
③ Bọc packet vào frame dst = MAC next hop
```

Xem kernel chọn gì:

```bash
ip route get 10.66.20.12
# 10.66.20.12 via 10.66.10.1 dev veth-a src 10.66.10.11
#             ^^^^^^^^^^^^^^ có "via" → sẽ ARP 10.66.10.1

ip route get 10.66.10.12
# 10.66.10.12 dev veth-a src 10.66.10.11
#             không có "via" → on-link → ARP thẳng 10.66.10.12
```

> Destination IP **bên trong packet** luôn là đích cuối. Chỉ địa chỉ được ARP hỏi mới thay đổi.

## 4. Một lần ARP diễn ra thế nào

```text
 A (192.168.1.10, aa:aa)                         B (192.168.1.20, bb:bb)
   │ ARP Request  dst ff:ff:ff:ff:ff:ff                 │
   │ "who-has 192.168.1.20 tell 192.168.1.10" ─────────►│ (broadcast: mọi host trong VLAN nhận)
   │                                                    │
   │◄──────── ARP Reply  dst aa:aa (unicast)            │
   │          "192.168.1.20 is-at bb:bb"                │
   │                                                    │
   │ lưu 192.168.1.20 → bb:bb vào neighbor cache        │
   │ ICMP/TCP trong frame dst bb:bb ───────────────────►│
```

## 5. Neighbor cache và các trạng thái

```bash
ip neigh show dev ens33
# 192.168.1.1  lladdr gg:gg:gg:00:00:01 REACHABLE
# 192.168.1.20 lladdr bb:bb:bb:00:00:02 STALE
# 192.168.1.99 FAILED
```

| Trạng thái | Nghĩa | **Chưa** chứng minh |
|---|---|---|
| `INCOMPLETE` | Đã gửi request, đang chờ reply | — |
| `REACHABLE` | Vừa xác nhận neighbor ở tầng link | TCP port mở, HTTP khỏe |
| `STALE` | Mapping cũ, sẽ xác nhận lại khi dùng | **Không phải lỗi** |
| `DELAY` / `PROBE` | Đang xác nhận lại | — |
| `FAILED` | Hết lượt hỏi, không ai trả lời | *Nguyên nhân* (cáp, VLAN, IP sai, host tắt…) |

Vì cache làm lần test đầu và lần sau khác nhau, **ghi trạng thái neighbor cùng lúc với capture**.

---

## 6. Thử suy luận: đổi prefix đổi cả hành vi ARP

A `10.1.1.10`, B `10.1.2.20/24`, gateway của A là `10.1.1.1`. A và B ở hai VLAN khác nhau.

| Cấu hình A | A nghĩ B ở đâu? | A ARP ai? | Kết quả |
|---|---|---|---|
| `10.1.1.10/24` | Ngoài subnet (`10.1.1.0/24`) | Gateway `10.1.1.1` | ✅ Đi qua router |
| `10.1.1.10/16` | Cùng subnet (`10.1.0.0/16`) | **B trực tiếp** | ❌ B ở VLAN khác, không nghe thấy → `FAILED` |

Cả hai địa chỉ đều "hợp lệ", nhưng prefix khác làm route on-link khác → hành vi ARP khác.

---

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Gửi tới server ngoài subnet thì ARP server đó." | ARP **gateway**. |
| "`STALE` là lỗi, phải flush." | `STALE` là bình thường; kernel tự xác nhận khi dùng lại. |
| "`REACHABLE` là service OK." | Chỉ chứng minh link-layer; port và app còn phải kiểm riêng. |
| "Router sẽ chuyển ARP sang subnet bên kia." | ARP là broadcast L2, **không** qua router. |

## Tự kiểm tra

1. `ip route get 8.8.8.8` trả `via 192.168.1.1 dev ens33`. ARP sẽ hỏi IP nào?
2. Entry `FAILED` nói gì và *không* nói gì?
3. A `10.0.0.10/8`, muốn tới `10.200.0.5`. Không có route nào khác. A ARP ai?

<details>
<summary>Đáp án</summary>

1. `192.168.1.1`.
2. Nói: resolution trên link thất bại (không ai trả lời). Không nói: vì sao — cần kiểm link, VLAN, IP đích, host đích.
3. ARP trực tiếp `10.200.0.5` vì `/8` làm nó on-link.

</details>

## Nguồn

- [RFC 826 — ARP](https://www.rfc-editor.org/rfc/rfc826)
- [ip-neighbour(8)](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html)
