# N04 Ví dụ — Cùng bridge, khác VLAN

> **Mục tiêu:** theo một frame đi qua bridge có VLAN filtering, rồi giải thích một lỗi PVID.

## Bối cảnh

```text
            ┌──────────────── br-w6 (vlan_filtering 1) ────────────────┐
            │  port A1-h    port A2-h    port B1-h    port B2-h         │
            │  VLAN 10      VLAN 10      VLAN 20      VLAN 20           │
            └─────┬────────────┬────────────┬────────────┬──────────────┘
                  A1           A2           B1           B2
            10.66.10.11  10.66.10.12  10.66.20.11  10.66.20.12
```

Mọi port là **access** (`pvid untagged`).

## Hành trình một frame: A1 → A2

```text
① A1 gửi frame KHÔNG tag (A1 không biết VLAN)
② Vào port A1-h → bridge gán VLAN 10 (PVID)
③ Tra FDB: dst MAC thuộc VLAN 10 ở port nào?
     ├─ biết  → chỉ gửi ra port đó
     └─ chưa  → flood ra mọi port VLAN 10 (A2-h), KHÔNG ra B1-h/B2-h
④ Ra port A2-h → bỏ tag (untagged) → A2 nhận frame thường
⑤ A2 trả lời → bridge học (MAC A2, port A2-h, VLAN 10)
```

ARP broadcast từ A1 chỉ flood trong VLAN 10 — B1/B2 không bao giờ thấy, dù cắm cùng bridge.

## Lỗi: PVID sai một port

| Port | Cấu hình đúng | Cấu hình lỗi |
|---|---|---|
| A1-h | `vid 10 pvid untagged` | `vid 20 pvid untagged` ❌ |
| A2-h | `vid 10 pvid untagged` | `vid 10 pvid untagged` |

**Triệu chứng:** A1 ping A2 fail; `ip -n w6-a1 neigh` → `FAILED`; IP/route hoàn toàn đúng.

**Bằng chứng hai lớp:**

| Lớp | Lệnh | Thấy |
|---|---|---|
| L2 config | `bridge vlan show` | A1-h ở VLAN 20, A2-h ở VLAN 10 |
| Packet | `tcpdump -eni w6-a1-h arp` + `tcpdump -eni w6-a2-h arp` | ARP request ở A1-h, **không** tới A2-h |

**Sửa tối thiểu:**

```bash
sudo bridge vlan del dev w6-a1-h vid 20
sudo bridge vlan add dev w6-a1-h vid 10 pvid untagged
```

**Verify:** `bridge vlan show` đúng → ping A1→A2 OK → `bridge fdb show` có MAC A1 ở VLAN 10.

---

## Ghi chú về capture

- Capture ở **endpoint/access port** thường thấy frame **không tag**.
- Capture trên **trunk/tagged port** mới thấy 802.1Q tag (`tcpdump -e` hiện `vlan 10`).
- Chọn capture point trước khi giải thích vì sao có/không có tag.

## Muốn A1 nói chuyện với B1?

Cần **một router L3** có interface trong cả VLAN 10 và VLAN 20, route ở endpoint và bật forwarding. Thêm IP cùng subnet ở hai VLAN **không** làm bridge nối chúng.

## Tự kiểm tra

Bạn đặt tạm cho A1 thêm IP `10.66.20.99/24` rồi ping B1 `10.66.20.11`. Kết quả mong đợi là gì, và nó chứng minh điều gì?

<details>
<summary>Đáp án</summary>

Ping **fail**, neighbor `10.66.20.11` → `FAILED`. Vì route lúc này on-link nên A1 thật sự gửi ARP — và ARP không vượt VLAN. Đây là phép thử đúng cho **VLAN isolation** (thay vì ping hai subnet khác nhau, vốn fail sớm ở route lookup và không chứng minh gì về VLAN).

</details>
