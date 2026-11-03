# N02 Bài 2 — IPv6 Neighbor Discovery và chẩn đoán neighbor

> **Sau bài này bạn sẽ:**
> - So sánh ND (IPv6) với ARP (IPv4) và biết lọc capture cho đúng.
> - Hiểu vì sao **không được chặn hết ICMPv6**.
> - Đọc capture request/reply theo cặp để khoanh vùng lỗi neighbor.
>
> **Cần trước:** [Bài 1 — ARP](./01-arp-and-neighbor-cache.md).

---

## 1. ARP vs ND — bảng so sánh

| | IPv4 — ARP | IPv6 — ND |
|---|---|---|
| Chạy trên | Trực tiếp trên Ethernet (EtherType `0x0806`) | **ICMPv6** (bên trong IPv6) |
| Hỏi | ARP Request | **Neighbor Solicitation (NS)** |
| Trả lời | ARP Reply | **Neighbor Advertisement (NA)** |
| Gửi hỏi tới | Broadcast `ff:ff:ff:ff:ff:ff` | **Solicited-node multicast** (`ff02::1:ffXX:XXXX`) |
| Tìm router | Không (cấu hình/DHCP) | **Router Solicitation / Advertisement (RS/RA)** |
| Kiểm trùng IP | Không có sẵn | **DAD** (Duplicate Address Detection) |
| Lọc tcpdump | `arp` | `icmp6` |

> Lọc `arp` sẽ **bỏ lỡ toàn bộ ND**. Dùng `'arp or icmp6'` khi lab có cả hai stack.

## 2. Các khái niệm IPv6 cần biết

- **Link-local `fe80::/10`**: mọi interface IPv6 đều có, chỉ dùng trên một link. Khi truy cập phải chỉ rõ interface: `ping fe80::1%ens33`.
- **Router Advertisement (RA)**: router quảng bá prefix và default router; host có thể tự cấu hình địa chỉ (SLAAC). RA **không phải** DNS response — DNS có thể đến qua RA option hoặc DHCPv6, tùy mạng.
- **DAD**: trước khi dùng một IPv6 address, host gửi NS hỏi "có ai dùng địa chỉ này chưa?".

> Vì NS/NA/RA/DAD đều là ICMPv6, **chặn hết ICMPv6 bằng firewall sẽ làm IPv6 hỏng**.

## 3. Hai stack, hai bài toán

- IPv4 chạy, IPv6 fail → kiểm **từng stack riêng**. Nhiều ứng dụng thử IPv6 trước, nên IPv6 hỏng có thể gây chậm/timeout dù IPv4 ổn.
- IPv6 đi được bằng địa chỉ nhưng tên không resolve → tách ND/route khỏi **resolver**.

```bash
ip -6 addr show dev ens33
ip -6 route
ip -6 neigh show dev ens33
sudo tcpdump -ni ens33 'icmp6'
```

---

## 4. Quy trình chẩn đoán neighbor

```text
Ping cùng subnet fail
   │
   ├─ ① Address/prefix đúng?          ip addr, ip route get
   │
   ├─ ② Neighbor state?               ip neigh
   │      ├─ FAILED      → bước ③
   │      └─ REACHABLE   → neighbor OK, chuyển sang route/firewall/listener
   │
   └─ ③ Capture theo cặp request/reply
```

### Đọc capture theo cặp

| Quan sát | Nghi ngờ | Kiểm |
|---|---|---|
| Request **không** rời host | Interface, route, capture point | `ip -br link`, `ip route get`, đổi `-i` |
| Request có, **không** có reply | Đích sai IP, khác L2/VLAN, firewall chặn ND | IP đích, `bridge vlan show`, firewall |
| Reply có, neighbor **không** cập nhật | MAC/IP trong message lạ, interface, duplicate | Đọc kỹ nội dung reply |
| Mapping **dao động** giữa 2 MAC | **Duplicate IP** | So capture/neigh trên nhiều host |

### Duplicate IPv4

Hai máy cùng IP → ARP reply đến từ hai MAC, mapping nhảy qua lại, kết nối chập chờn. **Không** "sửa" bằng static ARP: nguyên nhân gốc là cấp phát IP sai — phải tìm và sửa nguồn cấp phát.

---

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "IPv6 cũng dùng ARP." | Không; IPv6 dùng ND qua ICMPv6. |
| "Chặn ICMPv6 cho an toàn." | Làm hỏng ND/RA/DAD và Path MTU. |
| "RA cung cấp DNS server." | RA chủ yếu cung cấp prefix/router; DNS tùy mạng (RA option hoặc DHCPv6). |
| "Static ARP sửa được duplicate IP." | Chỉ che triệu chứng. |

## Tự kiểm tra

1. Bạn capture `tcpdump -ni ens33 arp` trên mạng IPv6-only và không thấy gì. Vì sao?
2. `ping fe80::1` báo lỗi "Invalid argument". Thiếu gì?
3. Request có, reply không. Hai nguyên nhân hay gặp nhất?

<details>
<summary>Đáp án</summary>

1. IPv6 dùng ND (ICMPv6), không dùng ARP; phải lọc `icmp6`.
2. Thiếu zone/interface: `ping fe80::1%ens33`.
3. Đích khác VLAN/L2 (không nghe được) hoặc IP đích sai/không tồn tại; ngoài ra firewall chặn ND.

</details>

## Nguồn

- [RFC 4861 — IPv6 Neighbor Discovery](https://www.rfc-editor.org/rfc/rfc4861)
- [RFC 4862 — IPv6 SLAAC & DAD](https://www.rfc-editor.org/rfc/rfc4862)
