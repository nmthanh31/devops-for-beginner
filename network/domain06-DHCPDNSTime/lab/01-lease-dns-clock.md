# N06 Lab — Cấu hình được cấp, tên và giờ

| | |
|---|---|
| **Thời lượng** | 60 phút |
| **Môi trường** | VM lab (chỉ đọc cấu hình; không sửa DNS, không đổi clock) |
| **Mục tiêu** | Xác định nguồn cấu hình mạng, so `getent`/`dig`, đọc TTL, giải thích trạng thái thời gian |

## Bước 1 — Baseline cấu hình

```bash
ip -br addr
ip route
resolvectl status
timedatectl
ls /etc/netplan/ 2>/dev/null; nmcli -t dev show 2>/dev/null | head
```

| Mục | Giá trị | Nguồn (DHCP / static / file nào?) |
|---|---|---|
| IP/prefix | | |
| Gateway | | |
| DNS server | | |
| Search domain | | |

> Tìm file Netplan/NetworkManager đang là nguồn trước khi kết luận "do DHCP cấp". Lease DHCP: `networkctl status <iface>` hoặc `/run/systemd/netif/leases/`.

## Bước 2 — So `getent` và `dig`

Chọn một tên công cộng được phép kiểm (ví dụ `example.com`).

```bash
getent ahosts example.com
dig example.com
dig @<DNS_SERVER> example.com
dig example.com | grep -A2 'ANSWER SECTION'   # cột thứ 2 là TTL
```

Chạy `dig` hai lần cách nhau 10 giây. TTL thay đổi thế nào? Giải thích.

Thêm test NSS: thêm tạm vào `/etc/hosts` một dòng `10.99.99.99 n06-test.example` → so `getent ahosts n06-test.example` với `dig n06-test.example` → **xóa dòng đó**.

## Bước 3 — Negative test

```bash
dig n06-khong-ton-tai.invalid
getent ahosts n06-khong-ton-tai.invalid; echo "exit=$?"
```

**Kết quả mong đợi:** `status: NXDOMAIN` — có câu trả lời, tên không tồn tại. `getent` exit code `2`.

## Bước 4 — Thời gian

Từ `timedatectl`, viết giải thích:

1. Local time vs UTC lệch bao nhiêu, do đâu?
2. "System clock synchronized" và "NTP service" đang ra sao?
3. Kiểm cert một site: `openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -dates` → so với `date -u`.

---

## Definition of Done

- [ ] Bảng baseline có cột nguồn cấu hình.
- [ ] So `getent`/`dig`, có ví dụ `/etc/hosts` thắng DNS (và đã dọn).
- [ ] Giải thích TTL giảm dần.
- [ ] NXDOMAIN evidence + giải thích khác timeout.
- [ ] Giải thích local/UTC/timezone/NTP + so validity cert.

## Cleanup

Xóa dòng `n06-test.example` khỏi `/etc/hosts`. Không có tài nguyên khác.
