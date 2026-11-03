# N01 Ví dụ — Một request qua gateway thay đổi những gì?

> **Mục tiêu:** tự dự đoán header ở từng link trước khi đọc đáp án, rồi đối chiếu với capture thật trong lab.

## Bối cảnh

```text
 Client                      Router                        Server
 10.1.1.10/24               ┌───────┐                    10.2.2.20:80
 MAC aa:aa  ─── link 1 ─── gg:gg   rr:rr ─── link 2 ───  MAC ss:ss
                 10.1.1.1   └───────┘   10.2.2.1
```

Client mở TCP tới `10.2.2.20:80`, OS chọn source port `53000`, gửi SYN.

> ✋ **Dừng lại và dự đoán** 3 cặp (MAC, IP, port) trên link 1 và link 2 trước khi đọc tiếp.

---

## Bước 1 — Client quyết định gửi cho ai

1. `10.2.2.20` **không** thuộc `10.1.1.0/24` → không on-link.
2. Route table có `default via 10.1.1.1` → next hop là gateway.
3. Client ARP hỏi MAC của **`10.1.1.1`** (không hỏi `10.2.2.20`) → nhận `gg:gg`.

## Bước 2 — Frame trên link 1

```text
Ethernet: aa:aa     → gg:gg       ← tới gateway
IP:       10.1.1.10 → 10.2.2.20   ← vẫn là server
TCP:      53000     → 80, SYN
TTL:      64
```

## Bước 3 — Router chuyển tiếp

1. Bóc Ethernet header, đọc IP đích `10.2.2.20`.
2. Tra route: `10.2.2.0/24` connected trên interface `rr:rr`.
3. ARP hỏi MAC của `10.2.2.20` → `ss:ss`.
4. Giảm TTL 64 → 63, bọc vào **frame mới**.

## Bước 4 — Frame trên link 2

```text
Ethernet: rr:rr     → ss:ss       ← ĐỔI
IP:       10.1.1.10 → 10.2.2.20   ← giữ nguyên
TCP:      53000     → 80, SYN     ← giữ nguyên
TTL:      63                      ← giảm 1
```

## Bước 5 — Chiều về

Server trả SYN-ACK `10.2.2.20:80 → 10.1.1.10:53000`. Server cần **route về** `10.1.1.0/24` (ở đây qua default gateway `10.2.2.1`). Thiếu route về là lỗi rất hay gặp — học kỹ ở [N05](../../domain05-RoutingReturnPath/README.md).

---

## Tóm tắt

| Trường | Link 1 | Link 2 | Đổi? |
|---|---|---|---|
| Src MAC | `aa:aa` | `rr:rr` | ✅ đổi |
| Dst MAC | `gg:gg` | `ss:ss` | ✅ đổi |
| Src/Dst IP | `10.1.1.10 → 10.2.2.20` | giống | ❌ |
| Src/Dst port | `53000 → 80` | giống | ❌ |
| TTL | 64 | 63 | ✅ giảm 1 |

## Đọc capture hai link

| Quan sát | Diễn giải |
|---|---|
| IP/port giữ nguyên, MAC khác | **Bình thường** — routing đúng |
| IP hoặc port đổi | Có **NAT** ([N09](../../domain09-FirewallConntrackNAT/README.md)) hoặc **proxy** |
| Hai phía có hai TCP connection khác hẳn | **Reverse proxy** ([N08](../../domain08-HTTPTLSReverseProxy/README.md)) tạo connection mới |

## Tự kiểm tra

1. Nếu server ở cùng subnet `10.1.1.0/24` (ví dụ `10.1.1.20`), destination MAC trên frame đầu là của ai?
2. Router có thay đổi source port không (không có NAT)?
3. Một packet có TTL 64 đi qua 3 router. TTL khi tới đích là bao nhiêu?

<details>
<summary>Đáp án</summary>

1. MAC của **server** (client ARP trực tiếp `10.1.1.20`); gateway không tham gia.
2. Không.
3. **61**.

</details>
