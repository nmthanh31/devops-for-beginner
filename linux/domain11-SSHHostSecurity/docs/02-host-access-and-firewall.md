# Bài 2 — Quyền truy cập, dịch vụ và host firewall

> **Sau bài này bạn sẽ:**
> - Tách 3 câu hỏi: service **listen** chưa? packet **được cho qua** chưa? user **được phép** chưa?
> - Đọc bind address và giảm bề mặt truy cập.
> - Thay đổi firewall trên VM đang SSH **mà không tự khóa mình**.
>
> **Cần trước:** [Bài 1](./01-ssh-trust-and-authentication.md).

---

## 1. Ba câu hỏi, ba bề mặt

| Câu hỏi | Bề mặt | Lệnh |
|---|---|---|
| Service có listen? | Socket | `ss -lntp` |
| Packet có tới và được cho qua? | Route + firewall | `ip route get`, `ufw status`, `nft list ruleset` |
| User có được đăng nhập? | sshd + account + key | `sshd -T`, `authorized_keys` |

```text
service active ≠ listen đúng IP ≠ client ngoài tới được ≠ user xác thực được
```

## 2. Bind address và bề mặt truy cập

| Listener | Ai kết nối được |
|---|---|
| `127.0.0.1:22` | Chỉ nội bộ máy |
| `192.168.220.133:22` | Qua IP đó |
| `0.0.0.0:22` / `[::]:22` | Mọi IPv4 / IPv6 local — còn tùy route + firewall |

- Dừng/disable có chủ đích các dịch vụ không dùng (`systemctl disable --now`).
- **Đổi port SSH** chỉ đổi nơi listen, không tạo xác thực mạnh hơn.

---

## 3. Firewall là gì

Firewall lọc packet theo địa chỉ, protocol, port, **trạng thái connection** và **thứ tự rule**.

```text
packet tới chính VM          → input    ← SSH vào VM đi đường này
packet VM tạo ra             → output
packet VM chuyển hộ máy khác → forward
```

| Verdict | Client thấy |
|---|---|
| `accept` | Kết nối bình thường |
| `drop` | Không gì → **timeout** |
| `reject` | Từ chối ngay → **refused** |

**Stateful:** rule cho kết nối mới vào port 22 → gói phản hồi thuộc connection đó được cho qua theo state `established` (học sâu ở [N09](../../../network/domain09-FirewallConntrackNAT/README.md)).

**UFW** là giao diện quản lý firewall trên Ubuntu (sinh rule nftables/iptables):

```bash
sudo ufw status verbose      # active? default policy?
sudo ufw status numbered     # rule theo thứ tự
```

> UFW `inactive` nghĩa rule UFW chưa áp dụng — **không** chứng minh không có firewall ở nơi khác (nft trực tiếp, Docker, cloud SG, VMware).

## 4. Thứ tự thay đổi an toàn trên VM đang SSH

```text
① Ghi IP/port hiện tại, GIỮ phiên SSH đang mở
② Có VMware console sẵn sàng (đường phục hồi)
③ Thêm đường truy cập mới (key) → test trong PHIÊN SSH MỚI
④ Sửa sshd → sudo sshd -t
⑤ Thêm rule allow SSH TRƯỚC → rồi mới bật policy deny
⑥ Test kết nối mới từ Windows (positive) + kết nối bị cấm (negative)
⑦ Chỉ đóng phiên cũ khi ⑥ PASS
```

```bash
sudo ufw allow 22/tcp          # hoặc: sudo ufw allow from 192.168.220.1 to any port 22 proto tcp
sudo ufw enable
```

> **Không** đặt policy `deny` trên host quản trị từ xa khi chưa có rule SSH và đường phục hồi.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "UFW chặn thì `ss` không còn thấy listener." | Listener vẫn còn; firewall chặn packet trước khi tới socket. |
| "Phiên SSH cũ vẫn chạy = rule mới cho phép." | Phiên cũ là `established`; phải test phiên **mới**. |
| "UFW inactive = không firewall." | Có thể có lớp khác. |

## Tự kiểm tra

1. UFW deny 22 với `drop`. Client Windows thấy gì? `ss -lntp` trên VM thấy gì?
2. Vì sao phải thêm rule allow trước khi `ufw enable`?

<details>
<summary>Đáp án</summary>

1. Client timeout; `ss` vẫn thấy sshd LISTEN.
2. `enable` áp default policy deny incoming ngay — nếu chưa có allow SSH, kết nối mới bị chặn (và tùy cấu hình có thể ảnh hưởng phiên hiện tại).

</details>

## Nguồn

- [LPIC-1 Topic 110](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [Ubuntu Server Firewall](https://ubuntu.com/server/docs/firewalls/)
