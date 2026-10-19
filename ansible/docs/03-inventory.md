# 03. Inventory, host pattern và biến kết nối

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Inventory là chương cần học trước playbook vì mọi thay đổi đều bắt đầu từ câu hỏi: “host nào sẽ bị tác động?”. Trước mỗi lệnh, hãy nhìn graph/list và xác nhận environment.

## 1. Inventory là gì?

Inventory là dữ liệu mô tả host, group, quan hệ group và cách Ansible kết nối. Nó không chỉ là danh sách IP.

```yaml
all:
  children:
    dev:
      hosts:
        dev-web:
          ansible_host: 192.0.2.11
    stag:
      hosts:
        stag-web:
          ansible_host: 192.0.2.12
    web:
      children:
        dev:
        stag:
```

Tên `dev-web` là alias logic; `ansible_host` là địa chỉ thật. Tách hai khái niệm giúp đổi IP mà không phải đổi toàn bộ playbook.

## 2. Group, child group và pattern

```text
all
├── dev
│   └── dev-web
├── stag
│   └── stag-web
└── web
    ├── dev
    └── stag
```

Pattern quyết định target:

| Pattern | Ý nghĩa |
|---|---|
| `all` | mọi host |
| `dev` | nhóm dev |
| `stag` | nhóm staging |
| `web` | group cha chứa dev/stag |
| `dev-web` | một host alias |
| `dev:!canary` | dev trừ canary |

Pattern sai có thể làm playbook không chạy host nào hoặc chạy quá rộng. `--list-hosts` là bước kiểm tra rẻ và nên có trong workflow.

## 3. Host variables và group variables

```text
inventories/lab/
├── hosts.yml
├── group_vars/dev.yml
├── group_vars/stag.yml
└── host_vars/dev-web.yml
```

Các biến kết nối phổ biến:

- `ansible_host`: IP/DNS thật;
- `ansible_user`: user SSH;
- `ansible_port`: SSH port;
- `ansible_ssh_private_key_file`: private key trên control node;
- `ansible_python_interpreter`: Python path nếu cần chỉ rõ.

Không đặt private key content hoặc password plaintext trong inventory.

## 4. INI và YAML inventory

INI ngắn gọn:

```ini
[dev]
dev-web ansible_host=192.0.2.11 ansible_user=labadmin

[stag]
stag-web ansible_host=192.0.2.12 ansible_user=labadmin

[web:children]
dev
stag
```

YAML phù hợp khi topology và biến lồng nhau phức tạp hơn. Không có định dạng tuyệt đối tốt hơn; điều quan trọng là parse được, review được và chạy đúng file.

## Lệnh cần chạy

**Git Bash/WSL — control node:**

```bash
ansible-inventory -i inventories/lab/hosts.yml --graph
ansible-inventory -i inventories/lab/hosts.yml --list
ansible-inventory -i inventories/lab/hosts.yml --host dev-web
ansible dev -i inventories/lab/hosts.yml -m ansible.builtin.ping
ansible stag -i inventories/lab/hosts.yml -m ansible.builtin.ping
```

## Thực hành cuối chương: chứng minh target

Tạo inventory có `dev/dev-web` và `stag/stag-web`, rồi chạy:

```bash
ansible all -i inventories/lab/hosts.yml -m ansible.builtin.command -a 'uname -a'
ansible dev -i inventories/lab/hosts.yml -m ansible.builtin.command -a 'free -h'
ansible stag -i inventories/lab/hosts.yml -m ansible.builtin.command -a 'df -h /'
```

Hoàn thành khi bạn chứng minh được output thuộc đúng environment, không chỉ khi lệnh trả về exit code 0.

## Tài liệu chính thức

- [How to build your inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
- [Patterns: targeting hosts and groups](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html)
- [Inventory variables](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#connecting-to-hosts-behavioral-inventory-parameters)

