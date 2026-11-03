# L11 — Lệnh cần nhớ

## Client

| Lệnh | Trả lời câu hỏi |
|---|---|
| `ssh-keygen -t ed25519 -f ~/.ssh/l11_lab_key` | Tạo cặp user key (`-t` loại key, `-f` file output) |
| `ssh -i KEY user@host` | Đăng nhập bằng private key nào? |
| `ssh -v -o BatchMode=yes -i KEY user@host true` | Key auth dừng ở bước nào? |
| `ssh-keygen -R host` | Xóa **đúng một** entry known_hosts (sau khi đã xác minh) |

## Server

| Lệnh | Trả lời câu hỏi |
|---|---|
| `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` | Fingerprint host key để đối chiếu |
| `sudo sshd -t` | Config hợp lệ về cú pháp? |
| `sudo sshd -T -C user=U,host=H,addr=A` | Config **hiệu lực** cho ngữ cảnh nào? |
| `sudo ss -lntp 'sport = :22'` | sshd có listener trên TCP 22? |
| `sudo journalctl -u ssh -n 50 --no-pager` | sshd ghi lỗi gì (`-n 50`: 50 dòng cuối)? |
| `namei -l PATH` | Quyền từng thành phần đường dẫn? |
| `stat -c '%U:%G %a %n' PATH` | Owner và mode? |

## Firewall (UFW)

| Lệnh | Trả lời câu hỏi |
|---|---|
| `sudo ufw status verbose` | Active? Default policy? |
| `sudo ufw status numbered` | Rule theo thứ tự? |
| `sudo ufw allow 22/tcp` | Thêm allow SSH (**trước** khi enable) |
| `sudo ufw delete N` | Xóa rule số N (rollback) |

> Không đổi firewall hoặc tắt password trong lab trước khi có key auth đã kiểm chứng **và** VMware console.
