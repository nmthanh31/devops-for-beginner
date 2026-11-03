# N09 Bài 1 — Firewall (nftables) và conntrack

> **Sau bài này bạn sẽ:**
> - Biết packet đi qua hook nào: **input / forward / output** — và sửa đúng chain.
> - Đọc cấu trúc nftables: table → chain (hook, priority, policy) → rule → verdict.
> - Hiểu conntrack state và vì sao rule `established,related` giữ đường phản hồi.
>
> **Cần trước:** [N05](../../domain05-RoutingReturnPath/README.md), [N07](../../domain07-TCPUDPICMP/README.md). Liên hệ [L11 host firewall](../../../linux/domain11-SSHHostSecurity/docs/02-host-access-and-firewall.md).

---

## 1. Hình dung: trạm kiểm soát có sổ ghi

Firewall là trạm gác đọc nhãn mỗi packet (IP, port, protocol, interface) rồi quyết định **cho qua / bỏ im lặng / từ chối**. Trạm gác **stateful** còn có **sổ ghi** (conntrack): "xe này đi ra lúc 10:01, giờ quay về — cho qua".

## 2. Packet đi qua hook nào

```text
                       ┌──────────► input ──► socket local (packet cho chính host)
packet vào ─► prerouting ┤
                       └──────────► forward ──┐  (router chuyển hộ)
                                              ▼
socket local ─► output ─────────────────► postrouting ─► packet ra
```

| Flow | Đi qua | Sửa chain nào |
|---|---|---|
| Client → web trên **chính host** | prerouting → **input** | `input` |
| Host tự gọi ra ngoài | **output** → postrouting | `output` |
| Router chuyển hộ client → server | prerouting → **forward** → postrouting | `forward` |

> Sửa nhầm chain là lỗi kinh điển: thêm rule `input` trên router để cho client đi qua — không có tác dụng, vì traffic đó đi `forward`.

## 3. Cấu trúc nftables

```text
table inet lab {                         ← table: container (family inet = IPv4+IPv6)
  chain fwd {                            ← base chain
    type filter hook forward priority 0; policy drop;   ← hook, thứ tự, mặc định
    ct state established,related accept               ← rule 1
    iifname "r-c" tcp dport 80 accept                  ← rule 2
    counter                                            ← đếm packet rơi xuống policy
  }
}
```

| Khái niệm | Ý nghĩa |
|---|---|
| **Table** | Container chứa chain/set |
| **Base chain** | Gắn vào **hook**, có **priority** (nhiều chain cùng hook xét theo priority) và **policy** (verdict nếu không rule nào kết thúc) |
| **Rule** | Điều kiện match + verdict, xét **theo thứ tự** |
| **Verdict** | `accept`, `drop`, `reject`, `jump`... |

```bash
sudo nft list ruleset -a     # -a hiện handle của từng rule
```

### Counter là bằng chứng — nhưng có giới hạn

Counter tăng ở rule nào → packet đã đi qua rule đó. Counter **không** tăng có thể vì: packet chưa tới hook, bị chain priority sớm hơn xử lý, hoặc không match điều kiện. Ghi hook, priority, policy, handle trước khi sửa.

---

## 4. Conntrack

Conntrack (thành phần Netfilter) theo dõi **flow** và gán state:

| State | Nghĩa |
|---|---|
| `new` | Packet bắt đầu flow (ví dụ SYN) |
| `established` | Flow đã thấy hai chiều |
| `related` | Liên quan flow đã có (ví dụ ICMP error, FTP data) |
| `invalid` | Không gán được flow hợp lệ |

```text
SYN  (new)          ─► rule "tcp dport 80 accept"           ✔
SYN-ACK (established) ◄─ rule "ct state established accept" ✔  ← nếu thiếu → client timeout
```

> `established` là trạng thái **network flow**, không có nghĩa app đã trả 200.

## 5. drop vs reject

| Verdict | Client thấy | Dùng khi |
|---|---|---|
| `drop` | Không gì → **timeout** | Không muốn lộ thông tin |
| `reject` | RST / ICMP unreachable → **refused** nhanh | Nội bộ, muốn fail nhanh |

Liên hệ [N07](../../domain07-TCPUDPICMP/docs/01-transport-behavior.md): timeout vs refused giờ có thêm nguồn gốc là firewall.

## 6. An toàn

- Đổi policy `input` trên host đang SSH có thể **tự khóa phiên**.
- Lab chạy trong **namespace**; tạo **table riêng**, xóa đúng table đó.
- **Không** `nft flush ruleset` trên host — xóa luôn firewall thật (kể cả của Docker).

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Rule input áp cho traffic đi xuyên router." | Đó là `forward`. |
| "Cho phép SYN là đủ." | Cần cho chiều về (`established`). |
| "Counter không tăng = rule sai." | Có thể packet chưa tới hook. |
| "drop và reject như nhau." | Timeout vs refused. |

## Tự kiểm tra

1. Router có `policy drop` ở forward, chỉ có rule `tcp dport 80 accept`. Client curl server:80 thấy gì? Vì sao?
2. Web chạy trên chính host bị chặn. Bạn sửa chain nào?

<details>
<summary>Đáp án</summary>

1. Timeout: SYN qua, nhưng SYN-ACK (source port 80, không phải dport 80) rơi vào policy drop. Thêm `ct state established,related accept`.
2. `input`.

</details>

## Nguồn

[nftables quick reference](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes) · [Connection tracking](https://wiki.nftables.org/wiki-nftables/index.php/Connection_Tracking_System) · [Netfilter hooks](https://wiki.nftables.org/wiki-nftables/index.php/Netfilter_hooks)
