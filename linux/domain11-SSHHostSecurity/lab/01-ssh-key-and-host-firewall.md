# L11 Lab — SSH key và host firewall

| | |
|---|---|
| **Thời lượng** | 75 phút |
| **Môi trường** | Windows client + VM lab (user `setup`). **Bắt buộc** mở sẵn VMware console |
| **Mục tiêu** | Key-only login có evidence; chứng minh firewall drop vs listener; rollback từng thay đổi |

## Phần A — Key auth

**A1. Tạo key lab riêng (Windows PowerShell):**

```powershell
ssh-keygen -t ed25519 -f $HOME\.ssh\l11_lab_key
```

**A2. Chép public key** (chỉ file `.pub`) vào VM:

```powershell
type $HOME\.ssh\l11_lab_key.pub | ssh setup@VM_IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

**A3. Kiểm quyền trên VM:**

```bash
namei -l ~/.ssh/authorized_keys
stat -c '%U:%G %a %n' ~ ~/.ssh ~/.ssh/authorized_keys
```

**A4. Test trong terminal Windows thứ hai (phiên mới):**

```powershell
ssh -v -o BatchMode=yes -i $HOME\.ssh\l11_lab_key setup@VM_IP true
```

**A5. Evidence cùng timestamp** trên VM: `sudo ss -lntp 'sport = :22'`, `sudo journalctl -u ssh -n 20 --no-pager` (tìm dòng `Accepted publickey for setup`).

**A6. Negative test có kiểm soát:** `ssh -o BatchMode=yes -i $HOME\.ssh\l11_lab_key root@VM_IP true` → dự đoán và giải thích kết quả.

## Phần B — Firewall: listener vs packet

**Dự đoán trước** (viết ra): nếu firewall drop TCP 22 từ Windows, `ss` trên VM còn hiện listener không? Client thấy gì?

```bash
sudo ufw status verbose
sudo ufw status numbered
sudo ss -lntp 'sport = :22'
```

**Nếu UFW đang inactive và bạn muốn thử** (chỉ khi có console):

```bash
sudo ufw allow from <WINDOWS_IP> to any port 22 proto tcp   # allow TRƯỚC
sudo ufw enable
sudo ufw status numbered
```

Positive: phiên **mới** từ Windows vẫn vào được. Negative: từ một nguồn khác (ví dụ namespace trên VM `ip netns` hoặc máy khác) tới port 22 → timeout.

**Rollback:** `sudo ufw disable` (hoặc `ufw delete N` với rule vừa thêm) → về trạng thái ban đầu đã ghi.

---

## Definition of Done

- [ ] Sơ đồ: client → route → firewall → sshd → user auth.
- [ ] `ssh -v` thành công bằng key + dòng `Accepted publickey` trong journal.
- [ ] Bảng quyền `~`, `~/.ssh`, `authorized_keys`.
- [ ] Một negative test có kiểm soát + giải thích.
- [ ] Giải thích vì sao `sshd -t` OK chưa chứng minh login được.
- [ ] Rollback cho **từng** thay đổi.

## Cleanup

Nếu muốn gỡ key lab: xóa dòng tương ứng trong `~/.ssh/authorized_keys` trên VM. Trả UFW về trạng thái ban đầu.
