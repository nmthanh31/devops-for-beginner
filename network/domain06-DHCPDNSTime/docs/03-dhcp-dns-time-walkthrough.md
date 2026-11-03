# N06 Ví dụ — Có IP rồi mà HTTPS vẫn lỗi

## Bối cảnh

VM nhận từ DHCP: `10.6.1.20/24`, gateway `10.6.1.1`, DNS `10.6.1.53`. `ip route get 10.6.1.53` → on-link ✅. Nhưng `getent ahosts app.lab` thất bại.

> ✋ Liệt kê 4 chỗ có thể sai trước khi đọc tiếp.

## Phần 1 — Lỗi tên

| # | Lệnh | Câu hỏi |
|---|---|---|
| 1 | `resolvectl status` | DNS thật của interface là `.53`, hay bị cấu hình khác ghi đè? |
| 2 | `dig @10.6.1.53 app.lab` | Server có trả `A/AAAA`? |
| 3 | `getent ahosts app.lab` | NSS có nhận cùng kết quả? |
| 4 | `grep app.lab /etc/hosts`; `grep hosts: /etc/nsswitch.conf` | Có mapping hoặc thứ tự nguồn khác? |

## Phần 2 — Tên đã OK, HTTPS lỗi

DNS trả đúng IP, nhưng:

```text
$ curl https://app.lab
curl: (60) SSL certificate problem: certificate is not yet valid
```

```bash
timedatectl
#   Universal time: Mon 2026-10-20 ...     ← lùi nhiều ngày so với thực tế
#   System clock synchronized: no
```

Cert có `notBefore` sau giờ hệ thống → client coi cert "chưa có hiệu lực". **Fix:** sửa đồng bộ clock (nguồn NTP), không cấp lại cert, không đổi timezone.

## Bài học

```text
DHCP cấp cấu hình được  ≠  DNS trả tên được  ≠  TLS xác thực cert được
```

Một bước PASS không làm các bước sau tự PASS.
