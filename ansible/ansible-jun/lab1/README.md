# Lab 00 — SSH key, inventory và Ansible ping

Lab này chỉ có một mục tiêu: hiểu đường đi từ control node tới managed node.

```text
SSH public key → SSH không password → inventory → ansible ping → whoami
```

Chưa cần playbook, role, template hay Vault.

## 1. Môi trường

Các lệnh sau chạy trong **WSL/Git Bash control node**. Thay giá trị nếu môi trường của bạn khác:

```text
User: setup
VM:   192.168.220.133
Key:  ~/.ssh/ansible_lab_ed25519
```

Project Ansible hiện tại nằm ở:

```text
D:\Documents\F\ansible\ansible-jun\jun
```

Trong WSL:

```bash
cd /mnt/d/Documents/F/ansible/ansible-jun/jun
```

## 2. Kiểm tra key

```bash
test -f ~/.ssh/ansible_lab_ed25519
test -f ~/.ssh/ansible_lab_ed25519.pub
chmod 600 ~/.ssh/ansible_lab_ed25519
```

Nếu chưa có key:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ansible_lab_ed25519
```

Không gửi file private key lên chat hoặc Git.

## 3. Copy public key vào VM

Lệnh này có thể hỏi password một lần:

```bash
ssh-copy-id -i ~/.ssh/ansible_lab_ed25519.pub setup@192.168.220.133
```

Nếu WSL/Git Bash không có `ssh-copy-id`, dùng fallback sau khi đăng nhập bằng password:

```bash
cat ~/.ssh/ansible_lab_ed25519.pub | \
  ssh setup@192.168.220.133 \
  'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys'
```

Public key được thêm vào VM; private key vẫn ở control node.

## 4. Chứng minh SSH không password

```bash
ssh -o BatchMode=yes \
  -i ~/.ssh/ansible_lab_ed25519 \
  setup@192.168.220.133 whoami
```

Kết quả mong đợi:

```text
setup
```

Nếu lệnh fail với `Permission denied`, key chưa được dùng đúng. Không chuyển sang bước Ansible khi bước này chưa pass.

## 5. Tạo inventory nhỏ

Từ project root `ansible/ansible-jun/jun`, tạo file:

```text
inventories/lab/lesson-00.ini
```

Nội dung:

```ini
[lab]
ansible-dev ansible_host=192.168.220.133 ansible_user=setup ansible_ssh_private_key_file=~/.ssh/ansible_lab_ed25519
```

## 6. Kiểm tra inventory

```bash
ansible-inventory -i inventories/lab/lesson-00.ini --graph
ansible-inventory -i inventories/lab/lesson-00.ini --host ansible-dev
```

Bạn cần nhìn thấy đúng alias `ansible-dev`, IP `192.168.220.133` và user `setup`.

## 7. Chạy Ansible ping và whoami

```bash
ansible lab -i inventories/lab/lesson-00.ini -m ansible.builtin.ping
ansible lab -i inventories/lab/lesson-00.ini -m ansible.builtin.command -a 'whoami'
```

Phân biệt:

```text
ssh ... whoami             → kiểm tra SSH trực tiếp
ansible ... -m ping        → kiểm tra Ansible/module/Python
ansible ... -m command ... → Ansible chạy command trên managed node
```

## Acceptance criteria

- [x] `ssh -o BatchMode=yes ... whoami` trả về `setup`.
- [x] `ansible-inventory --graph` hiển thị đúng một host.
- [x] Module `ansible.builtin.ping` trả về `pong`.
- [x] Ad-hoc `whoami` trả về `setup`.
- [x] Không copy private key vào VM.

## Khi có lỗi

Gửi đúng bốn thông tin sau, không gửi private key:

```text
Control node: WSL hay Git Bash?
Lệnh đã chạy:
Output lỗi:
Kết quả `ssh ... whoami` hiện tại:
```

## Tài liệu chính thức

- [Public key authentication](https://man.openbsd.org/ssh)
- [`ansible.builtin.ping`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ping_module.html)
- [Inventory guide](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)

