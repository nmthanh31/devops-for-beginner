# Bài 1 — SSH: định danh, mã hóa và xác thực

> **Sau bài này bạn sẽ:**
> - Tách hai câu hỏi xác thực: **client có đang nói đúng server không?** (host key) và **user là ai?** (user key/password).
> - Biết private key / public key nằm ở đâu, `known_hosts` và `authorized_keys` khác nhau thế nào.
> - Đọc thông báo lỗi để biết SSH đã đi tới giai đoạn nào.
>
> **Cần trước:** [L10 Host Networking](../../domain10-HostNetworking/docs/README.md) — IP/route đưa packet tới host, TCP đưa tới port 22.

---

## 1. Hình dung: vào tòa nhà có bảo vệ

1. Bạn kiểm biển tên tòa nhà có đúng không (**host key** — tránh vào nhầm nhà giả).
2. Bảo vệ kiểm thẻ của bạn (**user key**) với danh sách người được vào (**authorized_keys**).
3. Qua cổng, bạn làm việc với quyền của tài khoản mình (**UID/GID**).

## 2. Một phiên SSH đi qua những bước nào

```text
ssh client ──① TCP tới VM_IP:22──► sshd
           ◄─② server trình host key── client so với known_hosts
           ──③ thỏa thuận mã hóa ───►
           ──④ xác thực user (key/password) ─► server so với authorized_keys
           ◄─⑤ mở shell/command/SFTP với UID của user
```

| Thuộc tính | Bảo vệ khỏi |
|---|---|
| **Mã hóa** | Người khác đọc nội dung trên đường truyền |
| **Toàn vẹn** | Nội dung bị sửa giữa đường |
| **Xác thực server** (host key) | Kết nối nhầm máy giả mạo |
| **Xác thực user** | Người lạ đăng nhập |

---

## 3. Host key — client tin đúng server nào?

| | Nằm ở | Vai trò |
|---|---|---|
| Host **private** key | Server: `/etc/ssh/ssh_host_*_key` | Chứng minh danh tính server |
| Host **public** key | Server gửi cho client | Client lưu vào `~/.ssh/known_hosts` |

Lần sau kết nối, client so sánh. **Host key đổi đột ngột** có thể là: VM cài lại, server đổi key, hoặc bạn đang tới nhầm máy. Kiểm bằng kênh tin cậy (ví dụ VMware console):

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub     # chạy tại server: xem fingerprint
```

> **Không** xóa cả `known_hosts` để bỏ qua cảnh báo. Chỉ xóa đúng entry sau khi đã xác minh: `ssh-keygen -R VM_IP`.

## 4. User key — server tin user nào?

| | Nằm ở | Ghi chú |
|---|---|---|
| User **private** key | **Chỉ** trên client (`~/.ssh/l11_lab_key`) | Bảo vệ bằng passphrase; lộ là phải thu hồi |
| User **public** key | Server: `~home_của_user/.ssh/authorized_keys` | Không phải mật khẩu; đặt ở server không trao private key |

```text
client ký thử thách bằng private key
   ↓
server kiểm chữ ký bằng public key trong authorized_keys CỦA USER ĐANG LOGIN
   ↓
đăng nhập với UID/GID của tài khoản đó
```

- `ssh-agent` giữ private key đã mở khóa trong phiên làm việc.
- `authorized_keys` thuộc **user nhận đăng nhập**. Public key trong `/home/setup/.ssh/authorized_keys` **không** áp dụng cho `root@VM_IP` — username là một phần của phép kiểm.

## 5. Password vs key

| | Password | Public key |
|---|---|---|
| Bằng chứng | Mật khẩu (gửi trong kênh đã mã hóa) | Chữ ký từ private key |
| Directive | `PasswordAuthentication` | `PubkeyAuthentication` |

Hai cơ chế **độc lập**: tắt password trước khi key chạy được = **mất đường đăng nhập**.

Directive khác: `PermitRootLogin`, `AllowUsers`. Giá trị hiệu lực chịu ảnh hưởng của `Include` và `Match` → kiểm cấu hình thực tế trước khi sửa ([Bài 3](./03-safe-change-and-troubleshooting.md)).

## 6. Đọc lỗi theo giai đoạn

| Thấy | Đã qua | Chưa qua — kiểm |
|---|---|---|
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | TCP | Danh tính server — **chưa bàn tới authorized_keys** |
| `Permission denied (publickey)` | TCP, host key, mã hóa | Username, public key, policy server |

## 7. Một phiên SSH làm được gì

Shell (`ssh user@host`), một lệnh (`ssh user@host 'hostname'`), copy file (SFTP/SCP), **port forwarding**. Port forwarding tạo **đường truy cập mới** — không thay thế firewall policy, cần được hiểu và kiểm soát.

---

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Public key là bí mật." | Private key mới là bí mật. |
| "Key của setup dùng được cho root." | Mỗi user có `authorized_keys` riêng. |
| "Cảnh báo host key thì xóa known_hosts." | Xác minh fingerprint trước, xóa đúng entry. |
| "Đổi port SSH là bảo mật." | Chỉ đổi nơi listen, không tăng sức mạnh xác thực. |

## Tự kiểm tra

1. Bạn thấy `Permission denied (publickey)`. Có cần kiểm firewall không?
2. Private key lộ. Làm gì?
3. Vì sao không nên tắt `PasswordAuthentication` ngay khi vừa copy public key?

<details>
<summary>Đáp án</summary>

1. Không — TCP và SSH handshake đã thành công. Kiểm username, key, `authorized_keys`, quyền file, policy.
2. Xóa public key tương ứng khỏi `authorized_keys` trên mọi server, tạo cặp mới.
3. Chưa kiểm chứng key login trong **phiên mới**; nếu key lỗi sẽ tự khóa.

</details>

## Nguồn

- [LPIC-1 Topic 110](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0) · [LPIC-2 Objective 212.3](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
- [OpenSSH sshd_config(5)](https://man.openbsd.org/sshd_config.5)
