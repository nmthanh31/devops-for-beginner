# N09 Ví dụ — Một connection qua firewall và SNAT

## Bối cảnh

```text
Client 10.9.1.10 ── r-c 10.9.1.1 [Router: forward filter + SNAT] 10.9.2.1 r-s ── Server 10.9.2.20:80
```

Router SNAT subnet client thành `10.9.2.1`.

> ✋ Dự đoán tuple ở r-c và r-s.

## Tuple hai phía

```text
r-c (trước SNAT): 10.9.1.10:50000 → 10.9.2.20:80
r-s (sau SNAT):   10.9.2.1:PORT   → 10.9.2.20:80     (PORT có thể giữ 50000 hoặc đổi nếu trùng)
```

Server trả về `10.9.2.1:PORT` → router tra conntrack → chuyển về `10.9.1.10:50000`. Server **không cần** route về `10.9.1.0/24` (vì nó chỉ thấy `10.9.2.1`).

## Hai lỗi cùng triệu chứng "client timeout"

| | Lỗi A: forward chain drop | Lỗi B: thiếu SNAT + server không có route về |
|---|---|---|
| Capture r-c | SYN | SYN |
| Capture r-s | **Không** có SYN | SYN (src `10.9.1.10`), SYN-ACK **không** quay về r-s |
| `nft list ruleset -a` | Counter ở rule/policy drop tăng | Không có rule SNAT |
| `ip route get 10.9.1.10` trên server | — | Sai/không có |
| Fix | Thêm rule accept đúng flow | Thêm SNAT **hoặc** (tốt hơn nếu routing thuần) route về trên server |

Paired capture + route get phân biệt được hai lỗi mà chỉ nhìn client thì không.

> Counter tăng chứng minh **rule đã match**, chưa chứng minh app thành công. Kết hợp counter + capture + response.
