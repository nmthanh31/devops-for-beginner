# 01. Control node, managed node và SSH

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Chưa cần cài Ansible ngay. Hãy chứng minh đường truyền trước: control node SSH được vào hai managed node bằng key, chạy được `whoami`, và biết lỗi nằm ở Windows/WSL, network, SSH hay sudo.

## 1. Control node và managed node

Control node là nơi đặt project và chạy `ansible`, `ansible-playbook`. Managed node là máy đích được quản lý. Với lab này:

```text
WSL/Linux VM (control node)
       ├── SSH → ansible-dev
       └── SSH → ansible-stag
```

Control node không nhất thiết là máy production. Nó có thể là WSL, Linux VM, CI runner hoặc execution environment. Điều quan trọng là nó có network route, SSH client, private key và Ansible.

## 2. SSH key authentication

SSH key gồm public key và private key:

```text
control node: ~/.ssh/ansible_lab_ed25519       (bí mật)
managed node: ~/.ssh/authorized_keys           (public key)
```

Client ký challenge bằng private key; server kiểm tra public key. Private key không được copy sang managed node và không được commit.

Key authentication không loại bỏ host verification. `known_hosts` giúp control node biết host đang kết nối có đúng fingerprint đã tin cậy hay không. Chỉ tắt kiểm tra host key trong lab cô lập khi đã hiểu rủi ro.

## 3. User quản trị và sudo

Ansible thường đăng nhập bằng user thường rồi dùng `become: true` cho task cần root. Đây là ranh giới tốt hơn việc luôn đăng nhập trực tiếp bằng root.

```text
SSH user → task không cần root
         → sudo/become → package, /etc, service
```

Sudo password, nếu có, phải truyền qua cơ chế bảo mật; không đặt trong inventory plaintext.

## 4. Chuẩn bị lab không dùng cloud

Có thể dùng:

- hai VM Linux nội bộ;
- hai VM local qua VirtualBox/VMware/Hyper-V;
- hai container có SSH daemon;
- hai node Linux trong Kubernetes local nếu lab chỉ cần SSH/API tương ứng.

Container tối giản thường không có systemd. Vì vậy container phù hợp với file/package đơn giản nhưng không luôn phù hợp với bài service/Nginx cần init system.

## Cấu trúc file

```text
ansible/
├── inventories/lab/hosts.yml
├── .gitignore
└── README.md
```

## Các lệnh theo môi trường

**PowerShell:**

```powershell
wsl --status
wsl -l -v
```

**Git Bash/WSL — control node:**

```bash
hostname
ip addr
ssh-keygen -t ed25519 -f ~/.ssh/ansible_lab_ed25519
ssh -i ~/.ssh/ansible_lab_ed25519 labadmin@ansible-dev whoami
ssh -i ~/.ssh/ansible_lab_ed25519 labadmin@ansible-stag whoami
```

**Linux managed node:**

```bash
hostnamectl
ip addr
sudo -v
```

## Thực hành cuối chương: preflight SSH

Chỉ chuyển chương khi các điều kiện sau đúng:

- SSH key từ control node tới cả hai node thành công.
- Chạy `ssh -o BatchMode=yes ... whoami` không hỏi password.
- Hostname/IP không bị nhầm.
- User có thể dùng sudo theo policy của lab.

Khi lỗi, phân loại theo flow:

```text
DNS/IP → TCP/22 → SSH host key → user/key → sudo
```

## Tài liệu chính thức

- [Ansible connection methods](https://docs.ansible.com/ansible/latest/inventory/connection_details.html)
- [SSH authorized keys](https://man.openbsd.org/sshd)

