# 02. Cài đặt Ansible và cấu trúc project

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Mục tiêu không phải ghi nhớ mọi package. Hãy hiểu Ansible được cài ở control node, project quyết định inventory/config nào được dùng, và dependency có thể tái tạo được.

## 1. Ansible nằm ở đâu?

```text
Control node
├── Python + Ansible
├── ansible.cfg
├── inventory
├── playbooks/roles/
└── SSH private key (ngoài Git)

Managed node
└── SSH server + Python phù hợp
```

Ansible không cài thành agent trên managed node. Khi chạy module, control node có thể truyền code module tạm thời qua SSH rồi nhận JSON result.

## 2. Project layout

```text
ansible/
├── ansible.cfg
├── inventories/
├── playbooks/
├── roles/
├── collections/requirements.yml
├── docs/
├── README.md
└── .gitignore
```

`ansible.cfg` có thể đặt ở root project để inventory và `roles_path` nhất quán. Đừng phụ thuộc vào config global của user mà người khác không nhìn thấy.

```ini
[defaults]
inventory = inventories/lab/hosts.yml
roles_path = roles
retry_files_enabled = False

[privilege_escalation]
become_method = sudo
```

`become` nên bật có chủ đích ở play/task, tránh mọi task mặc định chạy root.

## 3. Collections và version

Module built-in thuộc `ansible.builtin`. Module ngoài có thể thuộc collection, ví dụ `kubernetes.core`. `requirements.yml` là manifest để cài collection, tương tự lock/requirements concept nhưng không thay thế việc pin version phù hợp.

```yaml
collections:
  - name: kubernetes.core
    version: '>=6.0.0,<7.0.0'
```

## 4. `.gitignore` và boundaries

```gitignore
*.pem
*.key
*_rsa
vault-password*
.ansible/
*.retry
*.log
__pycache__/
.venv/
```

`.gitignore` chỉ ngăn thêm nhầm; nó không làm secret đã commit biến mất khỏi history. Private key và Vault password phải nằm ngoài repository hoặc trong secret store.

## Lệnh cần chạy

**Git Bash/WSL — control node:**

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv openssh-client
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ansible ansible-lint yamllint
ansible --version
ansible-config dump --only-changed
ansible-galaxy collection install -r collections/requirements.yml
```

**Linux managed node:**

```bash
python3 --version
ssh -V
```

## Thực hành cuối chương: project preflight

Tạo README mô tả control node, tạo config và `.gitignore`, sau đó trả lời:

1. Lệnh Ansible đang chạy từ Python nào?
2. Inventory mặc định được lấy từ đâu?
3. Role được tìm trong path nào?
4. File nào tuyệt đối không được commit?

## Tài liệu chính thức

- [Installing Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [Ansible configuration settings](https://docs.ansible.com/ansible/latest/reference_appendices/config.html)
- [Ansible collections](https://docs.ansible.com/ansible/latest/collections_guide/index.html)

