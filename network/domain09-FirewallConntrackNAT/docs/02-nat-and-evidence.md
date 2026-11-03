# N09 Bài 2 — NAT: đổi địa chỉ thế nào, bằng chứng ở đâu

> **Sau bài này bạn sẽ:**
> - Phân biệt SNAT, DNAT, masquerade, port forwarding.
> - Biết DNAT xảy ra **trước** routing, SNAT **sau** routing.
> - Thiết kế capture filter theo tuple **tại điểm capture** (trước/sau NAT).
>
> **Cần trước:** [Bài 1](./01-firewall-conntrack.md).

---

## 1. Các loại NAT

| Loại | Đổi | Dùng cho | Hook (nft) |
|---|---|---|---|
| **SNAT** | Source IP/port | Nhiều host private đi ra ngoài qua một IP | `postrouting` |
| **Masquerade** | Source = IP hiện tại của egress | Như SNAT, khi IP egress động (DHCP) | `postrouting` |
| **DNAT** | Destination IP/port | Public endpoint → server nội bộ | `prerouting` |
| **Port forwarding** | DNAT một port cụ thể | `public:443 → 10.0.0.5:8443` | `prerouting` |

### Vì sao DNAT trước, SNAT sau?

```text
prerouting (DNAT: đổi đích) → ROUTING DECISION (dựa trên đích MỚI) → forward → postrouting (SNAT: đổi nguồn theo egress đã chọn)
```

- DNAT phải trước routing để packet được route tới **backend mới**.
- SNAT sau routing vì cần biết **egress** nào để chọn IP nguồn.

## 2. NAT dựa trên conntrack

```text
Client 10.1.0.10:40000 ─► Router ─► 203.0.113.20:443
                         SNAT: src → 198.51.100.5:50001
                         conntrack ghi: (10.1.0.10:40000 ↔ 198.51.100.5:50001)

Reply 203.0.113.20:443 → 198.51.100.5:50001
                         conntrack tra ngược → dst = 10.1.0.10:40000
```

Hệ quả:

- Chỉ **packet đầu** của flow đi qua rule NAT; các packet sau dùng ánh xạ đã lưu → **đổi rule chưa chắc sửa connection cũ** (cần `conntrack -D` hoặc chờ hết hạn).
- Return packet **phải đi qua đúng thiết bị giữ state**, nếu không không có ánh xạ ngược → client timeout. NAT cần **routing hai chiều + state ở đúng điểm**.

### Port forwarding — checklist

`public:443 → 10.0.0.5:8443` chạy được khi **cả 4** đúng:

- [ ] DNAT rule khớp.
- [ ] Backend có listener `:8443`.
- [ ] Firewall `forward` cho qua.
- [ ] Reply của backend quay về **qua NAT device** (default gateway backend trỏ đúng).

---

## 3. Bằng chứng

```bash
sudo nft list ruleset -a
sudo conntrack -L                      # cần gói conntrack; thiếu thì dùng ruleset + capture
ip route get DEST_IP
sudo tcpdump -ni IN_IF  host CLIENT_IP     # phía trước NAT
sudo tcpdump -ni OUT_IF host REMOTE_IP     # phía sau NAT
```

### Đọc hai cặp tuple

| Điểm capture | Tuple |
|---|---|
| Trước NAT (ingress) | `10.1.0.10:40000 → 203.0.113.20:443` |
| Sau NAT (egress) | `198.51.100.5:50001 → 203.0.113.20:443` |

> **Bẫy filter:** capture egress với `host 10.1.0.10` sẽ **không thấy gì** — source đã đổi. Thiết kế filter theo IP/port **tại điểm capture** (dùng `host 203.0.113.20` ở cả hai bên).

Source IP khác nhau ở hai capture = bằng chứng mạnh về chỗ NAT xảy ra.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Sửa rule NAT có hiệu lực ngay cho mọi connection." | Connection cũ giữ ánh xạ trong conntrack. |
| "DNAT xong là backend nhận được." | Còn forward, listener và đường về. |
| "Capture egress không thấy client IP = NAT sai." | Đúng ra là NAT đang chạy. |

## Tự kiểm tra

1. Port forward `:80 → 10.0.0.5:8080` OK, nhưng backend có default gateway là router khác. Client thấy gì?
2. Vì sao SNAT nằm ở postrouting?

<details>
<summary>Đáp án</summary>

1. Timeout — reply không qua NAT device nên không được dịch ngược (và client nhận packet từ IP lạ, nếu nhận được thì bỏ).
2. Cần biết egress interface (sau routing) để chọn source IP phù hợp.

</details>

## Nguồn

[nftables quick reference — NAT](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes) · [Ubuntu firewall masquerading](https://ubuntu.com/server/docs/firewalls/)
