# N01 Bài 2 — Switch chuyển frame ra đâu? Đọc capture theo lớp

> **Sau bài này bạn sẽ:**
> - Giải thích switch **học MAC** và quyết định forward/flood như thế nào.
> - Phân biệt **broadcast domain** với subnet IP.
> - Đọc một dòng `tcpdump -e` theo 3 lớp và biết ghi **capture point**.
>
> **Cần trước:** [Bài 1 — các lớp và đóng gói](./01-layers-and-frames.md).

---

## 1. Hình dung: người trực tổng đài học dần

Switch giống người trực tổng đài mới vào làm, không biết ai ngồi phòng nào:

- Mỗi khi có thư **gửi đi từ** phòng 3, anh ta ghi sổ: "người gửi X ở phòng 3".
- Khi có thư **gửi tới** X: tra sổ → đưa thẳng vào phòng 3.
- Chưa có X trong sổ → photo thư phát cho **mọi phòng** (trừ phòng gửi), ai đúng thì nhận.

Sổ đó chính là **MAC table / FDB** (Forwarding Database).

## 2. Cơ chế học MAC — từng bước

```text
       ┌──────── Switch ────────┐
 port1 │  A (aa:aa)             │
 port2 │  B (bb:bb)             │
 port3 │  C (cc:cc)             │
       └────────────────────────┘
```

| Bước | Sự kiện | Switch làm gì | FDB sau bước này |
|---|---|---|---|
| 1 | A gửi frame tới `bb:bb` vào port1 | Học `aa:aa → port1`. Chưa biết `bb:bb` → **flood** ra port2, port3 (*unknown unicast flooding*) | `aa:aa→p1` |
| 2 | B trả lời tới `aa:aa` vào port2 | Học `bb:bb → port2`. Biết `aa:aa` → gửi **chỉ** ra port1 | `aa:aa→p1`, `bb:bb→p2` |
| 3 | A gửi tiếp tới `bb:bb` | Biết → gửi **chỉ** ra port2. C không còn thấy | (giữ nguyên) |

Ba điểm cần nhớ:

1. Switch học từ **source MAC** của frame đi *vào*, không phải destination.
2. Switch **không biết IP**. Nó chỉ có bảng `MAC → port`. Ánh xạ `IP → MAC` là việc của ARP/ND trên host ([N02](../../domain02-ARPNeighborDiscovery/README.md)).
3. Entry có **tuổi thọ** (aging): không có traffic một thời gian thì bị xóa và lại flood.

## 3. Broadcast domain

**Broadcast domain** = nhóm interface cùng nhận broadcast Layer 2 của nhau (ví dụ ARP request `ff:ff:ff:ff:ff:ff`).

- Switch/bridge phát broadcast ra mọi port **trong cùng VLAN**.
- **Router không chuyển broadcast** Layer 2 sang subnet khác.
- VLAN ([N04](../../domain04-NetnsVethBridgeVLAN/README.md)) chia một switch thành nhiều broadcast domain logic.

```text
Cùng subnet (A → B):
  A hỏi ARP MAC của B → frame dst = MAC B → switch tra FDB → port của B

Khác subnet (A → C ở subnet khác):
  A hỏi ARP MAC của gateway → frame dst = MAC gateway
  IP đích bên trong vẫn là C
```

> **Hệ quả quan trọng:** hai host cùng đặt IP trong `/24` nhưng **khác VLAN** sẽ ARP mãi không có reply. Sửa route trên host *không* giúp ARP vượt VLAN — lỗi nằm ở Layer 2.

---

## 4. Đọc capture theo lớp

```bash
sudo tcpdump -eni ens33 -c 10
```

| Cờ | Ý nghĩa |
|---|---|
| `-e` | Hiện link header (MAC) |
| `-n` | Không phân giải tên/port → thấy số thật, nhanh hơn |
| `-i ens33` | Chọn interface (capture `lo` sẽ không thấy frame của `ens33`) |
| `-c 10` | Dừng sau 10 packet |

Ví dụ một dòng output và cách tách lớp:

```text
10:01:02.123 aa:aa:aa:00:00:01 > bb:bb:bb:00:00:02, ethertype IPv4 (0x0800), length 74:
             10.66.10.11.49152 > 10.66.10.12.8080: Flags [S], seq 1000, ...
```

| Lớp | Đọc được |
|---|---|
| Ethernet | `aa:aa…01 → bb:bb…02`, EtherType IPv4 |
| IP | `10.66.10.11 → 10.66.10.12` |
| TCP | port `49152 → 8080`, `Flags [S]` = SYN |

Với **ARP** chỉ có cặp IP/MAC, không có port (ARP không chạy trên IP/TCP).

### Capture point — luôn ghi kèm

Một bản capture chỉ có nghĩa khi biết **chụp ở đâu**: host/namespace, interface, hướng, thời điểm.

```text
Client ──[điểm 1]── bridge/switch ──[điểm 2]── Server
```

| Điểm 1 | Điểm 2 | Kết luận |
|---|---|---|
| Thấy frame | Không thấy | Lỗi **giữa hai điểm**: port, VLAN, bridge |
| Thấy | Thấy, server không trả lời | Lỗi ở **server**: IP/prefix, firewall, listener |
| Không thấy | — | Client chưa gửi: route, interface, hoặc **capture sai interface** |

> Capture trên bridge có thể không hiện VLAN tag giống capture trên cổng trunk (kernel/offload xử lý tag). Đối chiếu thêm `bridge vlan show`.

---

## Lỗi thường gặp

| Triệu chứng | Nguyên nhân có thể | Bằng chứng |
|---|---|---|
| IP đúng nhưng không ping được gì | Interface `DOWN` / `NO-CARRIER` | `ip -br link` |
| Cùng CIDR mà ARP không reply | Khác VLAN | `bridge vlan show`, capture hai phía |
| `Network is unreachable` | IP đích ngoài subnet, không có gateway | `ip route get <đích>` |
| "Không thấy packet nào" | Capture sai interface | Kiểm lại `-i`, thử interface khác |

## Tự kiểm tra

1. Switch học `MAC → port` từ trường nào của frame?
2. Switch mới khởi động nhận frame có destination MAC chưa biết. Nó làm gì?
3. Hai host `10.0.0.5/24` và `10.0.0.6/24` cắm cùng switch nhưng khác VLAN. Ping được không? Vì sao?
4. Capture tại client thấy SYN đi ra, capture tại server không thấy gì. Nên nghi ngờ đoạn nào?

<details>
<summary>Đáp án</summary>

1. **Source MAC** của frame đi vào port.
2. **Flood** frame ra mọi port khác trong cùng VLAN.
3. Không. ARP request (broadcast) không vượt VLAN nên A không học được MAC của B.
4. Đoạn **giữa hai capture point**: port, VLAN, bridge, firewall trung gian — không phải listener trên server.

</details>

## Nguồn

- [Linux bridge documentation](https://docs.kernel.org/networking/bridge.html)
- [tcpdump(1)](https://www.tcpdump.org/manpages/tcpdump.1.html)
