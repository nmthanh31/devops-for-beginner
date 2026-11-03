# N03 Bài 1 — CIDR: tính network bằng bit

> **Sau bài này bạn sẽ:**
> - Đọc `/N` thành mask và số địa chỉ trong block.
> - Tính tay network, broadcast, host range của bất kỳ IPv4/prefix nào trong < 1 phút.
> - Biết vì sao "ba octet đầu giống nhau" **không** có nghĩa là cùng subnet.
>
> **Cần trước:** [N02 Bài 1](../../domain02-ARPNeighborDiscovery/docs/01-arp-and-neighbor-cache.md) — prefix quyết định on-link hay qua gateway.

---

## 1. Hình dung: số nhà và tên đường

`10.20.30.70/26` giống địa chỉ "đường + số nhà":

- **26 bit đầu** = tên đường (network prefix). Cùng đường → giao trực tiếp.
- **6 bit sau** = số nhà (host part).

Hai nhà khác đường thì phải qua "bưu cục" (gateway), dù số nhà trông gần nhau.

## 2. `/N` nghĩa là gì

IPv4 có **32 bit**. `/N` = N bit đầu là network, `32 − N` bit còn lại là host.

```text
10.20.30.70/26
00001010.00010100.00011110.01 000110
└────────── 26 bit network ──┘└ 6 host ┘
mask: 11111111.11111111.11111111.11 000000 = 255.255.255.192
```

**Network address = IP AND mask** (giữ bit network, xóa bit host về 0):

```text
  .70  = 01000110
AND .192 = 11000000
  = 01000000 = .64   → network 10.20.30.64
```

## 3. Bảng tra nhanh (octet cuối)

| Prefix | Mask (octet cuối) | Block size | Địa chỉ/block | Host dùng được |
|---|---|---|---|---|
| `/24` | `.0` | 256 | 256 | 254 |
| `/25` | `.128` | 128 | 128 | 126 |
| `/26` | `.192` | 64 | 64 | 62 |
| `/27` | `.224` | 32 | 32 | 30 |
| `/28` | `.240` | 16 | 16 | 14 |
| `/29` | `.248` | 8 | 8 | 6 |
| `/30` | `.252` | 4 | 4 | 2 |
| `/31` | `.254` | 2 | 2 | 2 (point-to-point, RFC 3021) |
| `/32` | `.255` | 1 | 1 | 1 (host route) |

Mẹo: **block size = 256 − mask octet**, hoặc `2^(32−N)`.

## 4. Phương pháp 4 bước (tính tay)

Ví dụ `10.20.30.70/26`:

| Bước | Làm gì | Kết quả |
|---|---|---|
| ① Block size | `2^(32−26) = 64` | 64 |
| ② Liệt kê boundary | 0, 64, 128, 192 | — |
| ③ Tìm block chứa IP | `.70` nằm trong `64–127` | network **`.64`** |
| ④ Broadcast & host | cuối block = `.127`; host = network+1 → broadcast−1 | broadcast **`.127`**, host **`.65–.126`** (62 host) |

> **"Trừ 2"** (network + broadcast) chỉ đúng với subnet IPv4 thông thường. `/31` dùng cả 2 địa chỉ cho link điểm-điểm; `/32` là đúng 1 địa chỉ.

---

## 5. Cùng subnet nghĩa là gì

Cùng subnet = địa chỉ đích nằm trong **prefix on-link theo cấu hình của máy nguồn**.

| | A `10.20.30.70/26` | B `10.20.30.130/26` |
|---|---|---|
| Network | `10.20.30.64` | `10.20.30.128` |
| Cùng subnet? | ❌ — ba octet đầu giống nhưng block khác |

A muốn tới B phải qua router. Không có route/default gateway → kernel báo `Network is unreachable`.

> **Bất đối xứng:** mỗi máy tự quyết theo *prefix của chính nó*. Nếu A là `/26` còn B là `/24`, A nghĩ B ở xa, B lại nghĩ A ở gần. Xem [ví dụ](./03-prefix-fault.md).

## 6. IPv6 — khác gì

- Cũng dùng prefix, thường `/64` cho một LAN.
- **Không có broadcast** kiểu IPv4 (dùng multicast) → **không áp "trừ 2"**.

---

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "`10.20.30.70` và `10.20.30.130` cùng mạng vì cùng `10.20.30`." | Phụ thuộc prefix; với `/26` là hai subnet. |
| "Biết IP là biết subnet." | Phải có prefix. |
| "Luôn trừ 2 host." | Không với `/31`, `/32`, IPv6. |

## Tự kiểm tra

Tính network / broadcast / host range:

1. `192.168.5.200/27`
2. `172.16.9.10/28`
3. `10.0.0.130/25`
4. `10.33.8.77/27` và `10.33.8.100/27` có cùng subnet không?

<details>
<summary>Đáp án</summary>

1. Block 32 → `192–223`: network `.192`, broadcast `.223`, host `.193–.222`.
2. Block 16 → `0–15`: network `.0`, broadcast `.15`, host `.1–.14`.
3. Block 128 → `128–255`: network `.128`, broadcast `.255`, host `.129–.254`.
4. `.77` thuộc `64–95`; `.100` thuộc `96–127` → **không** cùng subnet.

</details>

## Nguồn

- [RFC 4632 — CIDR](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 3021 — /31 point-to-point](https://www.rfc-editor.org/rfc/rfc3021)
- [LPIC-1 Objective 109.1](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
