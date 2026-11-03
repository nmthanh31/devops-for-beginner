# N03 Ví dụ — Hai host nhìn cùng địa chỉ theo hai cách

> **Mục tiêu:** thấy prefix lệch giữa hai đầu tạo ra đường đi **bất đối xứng** — chiều đi đúng, chiều về sai.

## Bối cảnh

| Host | Cấu hình | Network theo chính nó | Nghĩ host kia ở đâu? |
|---|---|---|---|
| A | `192.168.10.70/26` | `192.168.10.64–127` | B `.130` **ngoài** subnet → qua gateway |
| B | `192.168.10.130/24` | `192.168.10.0–255` | A `.70` **trong** subnet → ARP trực tiếp |

A và B ở hai VLAN khác nhau, nối nhau qua router.

## Diễn biến

```text
Chiều đi  : A ──► gateway ──► router ──► B         ✅ (A dùng route via gateway)
Chiều về  : B ──► ARP "who-has .70?" trong VLAN B   ❌ (A không ở VLAN B, không ai trả lời)
```

Triệu chứng: B **nhận** được ping/SYN của A nhưng A không bao giờ nhận reply. Capture tại B thấy request đến + ARP `who-has 192.168.10.70` lặp lại.

## Chứng minh: route get trên **cả hai** host

```bash
# Trên A
$ ip route get 192.168.10.130
192.168.10.130 via 192.168.10.65 dev eth0 src 192.168.10.70    ← qua gateway

# Trên B
$ ip route get 192.168.10.70
192.168.10.70 dev eth0 src 192.168.10.130                       ← on-link (sai)
```

Chỉ kiểm một đầu sẽ không bao giờ thấy lỗi.

## Sửa tối thiểu

Đưa B về prefix đúng theo address plan (ví dụ `192.168.10.130/26` với gateway `.129`), rồi verify:

1. `ip route get 192.168.10.70` trên B → có `via`.
2. Ping hai chiều thành công.
3. Capture B không còn ARP `who-has .70`.

> **Bài học:** prefix phải nhất quán với **topology** (VLAN/router), không chỉ "trông cùng dải 192.168.10.x".

---

## Bài luyện: tính nhanh `/27`

`/27` → 5 bit host → block `2^5 = 32`. Boundary octet cuối: `0, 32, 64, 96, 128, 160, 192, 224`.

`10.33.8.77/27`: `.77` thuộc `64–95` → network `.64`, broadcast `.95`, host `.65–.94`.

Sau khi tính tay, kiểm bằng công cụ (`ipcalc` hoặc `python3 -c "import ipaddress; print(ipaddress.ip_interface('10.33.8.77/27').network)"`). Nếu lệch, tìm bit/octet nhầm **trước** khi gắn IP thật.

## Tự kiểm tra

A `10.5.5.10/24`, B `10.5.5.200/25`. Ai nghĩ người kia on-link? Lỗi xảy ra ở chiều nào (giả sử hai host khác VLAN, có router)?

<details>
<summary>Đáp án</summary>

- A (`/24` → `.0–.255`): nghĩ B on-link → **A ARP trực tiếp B** → fail ngay chiều đi.
- B (`/25` → `.128–.255`): A `.10` ngoài subnet → qua gateway.

Lỗi ở **chiều đi** của A (A không bao giờ gửi được tới router).

</details>
