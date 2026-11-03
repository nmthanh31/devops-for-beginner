# N04 Bài 2 — Bridge, FDB và VLAN

> **Sau bài này bạn sẽ:**
> - Dùng Linux bridge như một switch L2 và đọc FDB.
> - Phân biệt **3 bảng**: FDB, neighbor, route.
> - Hiểu access port, trunk port, **PVID**, **untagged**, và lỗi hay gặp khi bật `vlan_filtering`.
>
> **Cần trước:** [Bài 1 — netns & veth](./01-netns-veth.md), [N01 Bài 2 — switch](../../domain01-EncapsulationEthernet/docs/02-switch-and-capture.md).

---

## 1. Linux bridge = switch phần mềm

Gắn interface làm **port** của bridge → frame vào một port được forward sang port khác theo **FDB** (bảng MAC đã học, giống N01).

```text
namespace A ── veth ──┐
                      br-n04  (switch)
namespace B ── veth ──┘
```

Hai namespace **cùng subnet** ping nhau được qua bridge mà **không cần IP trên bridge**. Điều kiện: bridge `UP`, mọi port `UP`, interface trong namespace `UP` và có IP/prefix đúng.

> Bridge **không route** giữa các subnet chỉ vì chúng cắm chung. Nó chỉ nhìn **MAC và VLAN**. Muốn đi giữa subnet cần router (L3).

## 2. Ba bảng — ba câu hỏi

| Bảng | Ở đâu | Ánh xạ | Câu hỏi | Lệnh |
|---|---|---|---|---|
| **Route table** | Host / namespace | prefix → next hop, interface | Gửi qua ai? | `ip route` |
| **Neighbor table** | Host / namespace | IP → MAC | MAC của next hop? | `ip neigh` |
| **FDB** | Bridge / switch | MAC (+VLAN) → port | Frame ra port nào? | `bridge fdb show` |

Nhầm ba bảng này là nguồn gốc của rất nhiều chẩn đoán sai.

---

## 3. VLAN 802.1Q

**VLAN** chia một switch thành nhiều **broadcast domain logic**. Frame mang **VLAN tag** (VLAN ID 1–4094) khi đi trên đường chung.

```text
Ethernet frame không tag: [dst MAC][src MAC][EtherType][payload]
Ethernet frame có tag:    [dst MAC][src MAC][0x8100 | VLAN ID][EtherType][payload]
```

### Access port vs trunk port

| | Access port | Trunk port |
|---|---|---|
| Nối tới | Endpoint (máy, namespace) không hiểu VLAN | Switch/router khác |
| Số VLAN | Một | Nhiều |
| Frame trên dây | **Không tag** | **Có tag** |

### PVID và untagged — hai chiều của access port

```text
            frame KHÔNG tag đi VÀO              frame ĐI RA endpoint
endpoint ───────────────────────────► port ─────────────────────────► endpoint
            bridge gán VLAN = PVID              bridge BỎ tag (untagged)
```

- **PVID** (Port VLAN ID): VLAN gán cho frame **không tag đi vào** port.
- **untagged**: khi gửi **ra** port, bỏ tag.

Access port VLAN 10 = `vid 10 pvid untagged`.

### Hậu quả

- Port PVID 10 và port PVID 20: ARP broadcast VLAN 10 **không** tới VLAN 20.
- **Lỗi hay gặp:** bật `vlan_filtering 1` mà quên membership ở một port → IP, route đều đúng nhưng bridge **âm thầm loại** frame.
- Ping hai VLAN khác nhau **vẫn thành công**? Có thể bạn vô tình tạo đường route/bridge ngoài ý muốn (ví dụ port còn VLAN 1 mặc định).

## 4. Lệnh quan sát

```bash
bridge link                  # port nào thuộc bridge nào, trạng thái
bridge fdb show br br-n04    # MAC đã học (theo VLAN nếu filtering)
bridge vlan show             # membership, PVID, untagged của từng port
ip -d link show br-n04       # chi tiết bridge (vlan_filtering ...)
```

Ví dụ đọc `bridge vlan show`:

```text
port              vlan-id
w6-a1-h           10 PVID Egress Untagged     ← access VLAN 10
w6-b1-h           20 PVID Egress Untagged     ← access VLAN 20
br-w6             1 PVID Egress Untagged      ← chính bridge (self)
```

---

## 5. Hai khái niệm "nhận diện là đủ"

- **STP** (Spanning Tree): chống loop L2 khi topology có đường vòng. Lab một bridge không tạo loop nên không cần. **Không** nối bridge lab vào NIC quản trị.
- **Bond / LACP** (802.1AX): gộp nhiều link để chịu lỗi/chia tải; hai đầu phải thống nhất. Bond **không** làm hai VLAN nói chuyện, **không** thay routing. Chỉ cần nhận ra khi thấy `bond0` trên host thật.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Cắm chung bridge thì mọi subnet nói chuyện được." | Bridge là L2; khác subnet cần router. |
| "Bridge cần IP mới chuyển frame." | Không; IP trên bridge chỉ cần nếu host muốn tham gia L3. |
| "Endpoint phải hiểu VLAN tag." | Access port gắn/bỏ tag thay endpoint. |
| "Bật vlan_filtering là xong." | Phải cấu hình membership/PVID từng port. |

## Tự kiểm tra

1. `ip neigh` của A có MAC của B, nhưng ping vẫn fail. `bridge fdb show` nên kiểm gì?
2. Port A1 `vid 10 pvid untagged`, port A2 `vid 20 pvid untagged`. A1 và A2 cùng `/24`. Ping được không?
3. Sau khi bật `vlan_filtering`, mọi ping đều fail. Nghi ngờ đầu tiên?

<details>
<summary>Đáp án</summary>

1. MAC của B có được học trên **đúng port** và **đúng VLAN** không.
2. Không — khác VLAN, ARP không qua.
3. Port chưa có membership/PVID đúng (hoặc chỉ còn VLAN 1 ở một số port) → kiểm `bridge vlan show`.

</details>

## Nguồn

- [Linux bridge documentation](https://docs.kernel.org/networking/bridge.html)
- [bridge(8)](https://man7.org/linux/man-pages/man8/bridge.8.html)
