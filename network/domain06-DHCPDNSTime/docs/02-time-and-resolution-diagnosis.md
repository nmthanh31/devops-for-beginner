# N06 Bài 2 — Vì sao đồng hồ ảnh hưởng network?

> **Sau bài này bạn sẽ:**
> - Phân biệt **UTC timestamp**, **timezone**, **clock sync**.
> - Biết clock lệch làm hỏng TLS, token, và việc đọc log.
> - Dùng bảng phân loại để tách lỗi DNS / NSS / clock / cache.
>
> **Cần trước:** [Bài 1](./01-dhcp-dns.md). Liên hệ [L07 Logs, time & timers](../../../linux/domain7-LogsTimeTimers/README.md).

---

## 1. Ba khái niệm dễ lẫn

| Khái niệm | Là gì | Đổi nó có sửa clock sai không? |
|---|---|---|
| **UTC timestamp** | Mốc thời gian tuyệt đối | — |
| **Timezone** | Cách *hiển thị* giờ địa phương | **Không** |
| **Clock sync (NTP/chrony)** | Làm mốc thời gian **đúng** | Có |

> So log nhiều máy: đưa về **UTC** trước. Máy lệch 10 phút có thể tạo ra log "response trước request".

## 2. Clock lệch làm hỏng gì

| Thành phần | Triệu chứng |
|---|---|
| TLS certificate | "not yet valid" (clock chậm) / "expired" (clock nhanh) |
| Token có hạn (JWT, AWS SigV4, Kerberos) | Bị từ chối |
| Điều tra sự cố | Log nhiều máy không khớp thứ tự |

## 3. Lệnh

```bash
timedatectl            # giờ local, UTC, timezone, "System clock synchronized: yes/no"
chronyc tracking       # nguồn và độ lệch (nếu dùng chrony)
date -u                # timestamp UTC cho evidence
```

NTP chưa sync → kiểm cấu hình nguồn, DNS/route tới nguồn, firewall UDP/123 **trước** khi chỉnh giờ tay.

> **An toàn lab:** không đổi clock thật của VM dùng chung để tạo fault. Mô phỏng bằng cách đọc validity của cert và so với `date -u`.

---

## 4. Bảng phân loại lỗi

| Quan sát | Ưu tiên kiểm |
|---|---|
| IP kết nối được, tên thất bại | NSS / DNS server / TTL |
| `dig @SERVER` được, `getent` không | NSS / local resolver / `/etc/hosts` |
| DNS trả IP đúng, HTTPS báo lỗi thời gian cert | Clock + validity cert |
| DNS trả IP cũ | TTL / cache / dữ liệu authoritative |

### Hai kỹ thuật tách lớp

**Kiểm cert so với giờ:**

```bash
date -u
openssl s_client -connect HOST:443 -servername NAME </dev/null 2>/dev/null \
  | openssl x509 -noout -dates
# notBefore=...   notAfter=...
```

**Bỏ qua DNS nhưng giữ hostname cho SNI/Host:**

```bash
curl --resolve NAME:443:IP https://NAME/
```

Nếu lệnh này chạy được → DNS là vấn đề; TLS và backend ổn.

## Tự kiểm tra

1. Đổi timezone từ UTC sang Asia/Ho_Chi_Minh có sửa được lỗi "certificate not yet valid" không?
2. `curl https://app.lab` lỗi resolve, `curl --resolve app.lab:443:10.6.1.30 https://app.lab` trả 200. Kết luận?

<details>
<summary>Đáp án</summary>

1. Không — timezone chỉ đổi hiển thị; phải sửa sync clock.
2. DNS/NSS là lỗi; TCP, TLS (đúng SNI) và HTTP backend đều ổn.

</details>

## Nguồn

[LPIC-1 108.1 & 109.4](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0) · [chrony docs](https://chrony-project.org/documentation.html)
