# Bài 3 — Thay đổi an toàn và chẩn đoán SSH

> **Sau bài này bạn sẽ:**
> - Phân loại lỗi SSH theo giai đoạn trước khi sửa.
> - Quan sát cùng lúc client (`ssh -v`) và server (`ss`, `journalctl`, `sshd -T`).
> - Sửa quyền file key đúng cách, không dùng `777`.
>
> **Cần trước:** [Bài 1](./01-ssh-trust-and-authentication.md), [Bài 2](./02-host-access-and-firewall.md), [L04 permissions](../../domain4-Identity&Permissions/docs/README.md).

---

## 1. Phân loại lỗi trước khi sửa

| Triệu chứng | Giai đoạn | Bề mặt kiểm |
|---|---|---|
| `Could not resolve hostname` | Trước TCP | DNS / hosts trên client |
| `Connection timed out` | TCP chưa lên | Route, firewall drop, VM network, return path |
| `Connection refused` | Host reachable | Không có listener / explicit reject |
| Host key changed | Sau TCP | Xác minh fingerprint |
| `Permission denied (publickey)` | Sau handshake | User, key, `authorized_keys`, quyền file, sshd policy |

### Đọc `ssh -v` như timeline

```text
debug1: Connecting to 192.168.220.133 port 22.     ← ① TCP
debug1: Connection established.                    ← TCP OK
debug1: Server host key: ssh-ed25519 SHA256:...    ← ② host key
debug1: Host '192.168.220.133' is known ...        ← khớp known_hosts
debug1: Offering public key: l11_lab_key ED25519   ← ④ client đưa key
debug1: Server accepts key ...                     ← server có public key tương ứng
Authenticated to 192.168.220.133                   ← xong
```

- Dừng ở `Connecting to ...` rồi timeout → chưa tới sshd; sửa `authorized_keys` **vô ích**.
- Tới `Offering public key` rồi `Permission denied` → mới kiểm phía server.

## 2. Quan sát nhiều lớp

**Client:**

```bash
ssh -v -o BatchMode=yes -i ~/.ssh/l11_lab_key setup@VM_IP true
```

`BatchMode=yes` không hỏi password → kết quả phản ánh đúng key path.

**Server:**

```bash
sudo ss -lntp 'sport = :22'
sudo systemctl status ssh --no-pager
sudo journalctl -u ssh -n 50 --no-pager      # đọc theo timestamp lần thử
sudo sshd -t                                 # chỉ kiểm cú pháp
```

> Không đăng private key hay toàn bộ log có dữ liệu nhạy cảm.

## 3. Cấu hình hiệu lực

`sshd_config` có thể `Include` các file trong `sshd_config.d/`, và `Match` áp chính sách khác theo user/IP/group.

```bash
sudo sshd -T -C user=setup,host=k8s-wk,addr=192.168.220.1 | grep -Ei 'passwordauth|pubkeyauth|permitroot|allowusers'
```

| Lệnh | Chứng minh |
|---|---|
| `sshd -t` | Config **hợp lệ về cú pháp** |
| `sshd -T -C ...` | Giá trị **hiệu lực** cho ngữ cảnh đó |
| Đăng nhập phiên mới | User **thật sự** vào được |

## 4. Quyền file key phía server

`StrictModes` (mặc định bật): sshd từ chối `authorized_keys` nếu home, `.ssh` hoặc file cho người khác ghi.

```bash
namei -l /home/setup/.ssh/authorized_keys
stat -c '%U:%G %a %n' /home/setup /home/setup/.ssh /home/setup/.ssh/authorized_keys
```

| Path | Owner | Quyền tối đa an toàn |
|---|---|---|
| `/home/setup` | setup | không cho group/other ghi (ví dụ `755`/`750`) |
| `~/.ssh` | setup | `700` |
| `authorized_keys` | setup | `600` |

> Đọc **thực tế** bằng `namei` trước khi sửa; không áp công thức mù, **không `chmod 777`**.

## 5. Sau khi sửa — verify hai chiều

- **Positive:** key login được trong **phiên mới**.
- **Negative:** phương thức/user cần cấm thật sự bị từ chối (ví dụ `ssh -o PubkeyAuthentication=no setup@VM_IP` → `Permission denied` nếu đã tắt password).

Giữ phiên cũ tới khi positive test từ Windows hoàn tất.

## Tự kiểm tra

1. `sshd -t` không báo lỗi. Đã chắc login được chưa?
2. `/home/setup` có quyền `777`. Key đúng nhưng `Permission denied`. Vì sao?

<details>
<summary>Đáp án</summary>

1. Chưa — chỉ chứng minh cú pháp; cần `sshd -T` và login phiên mới.
2. `StrictModes`: home cho người khác ghi → sshd từ chối dùng `authorized_keys`. Sửa về `755`/`750`.

</details>

## Nguồn

- [OpenSSH sshd_config(5)](https://man.openbsd.org/sshd_config.5)
- [LPIC-2 Objective 212.3](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
