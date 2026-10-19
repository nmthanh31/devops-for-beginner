# 10. Quản lý nhiều môi trường

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Hãy tách hai câu hỏi:

1. Code automation làm gì? — playbook/role dùng chung.
2. Chạy ở đâu và với dữ liệu nào? — inventory/group_vars theo environment.

Không copy playbook chỉ vì dev và stag có giá trị khác nhau.

## 1. Environment boundary

```text
same playbook + same roles
          ├── inventories/dev  → dev hosts + dev variables
          └── inventories/stag → stag hosts + stag variables
```

Inventory là boundary runtime; branch name không đủ để bảo vệ target. Lệnh CI/local phải chỉ rõ `-i` và nên có bước `--list-hosts`/guard.

## 2. Cấu trúc đề xuất

```text
ansible/
├── inventories/
│   ├── dev/
│   │   ├── hosts.yml
│   │   └── group_vars/all.yml
│   └── stag/
│       ├── hosts.yml
│       └── group_vars/all.yml
├── playbooks/site.yml
├── roles/
└── ansible.cfg
```

```yaml
# inventories/dev/group_vars/all.yml
app_environment: dev
app_port: 8080
```

```yaml
# inventories/stag/group_vars/all.yml
app_environment: stag
app_port: 8080
```

Secret không đặt ở đây; dùng Vault/secret manager.

## 3. Tránh deploy nhầm

Trước thay đổi:

```bash
ansible-inventory -i inventories/dev/hosts.yml --graph
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --list-hosts
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --check
```

Trong staging nên có manual approval, protected environment và credential/runner chỉ tới target staging.

## Thực hành cuối chương: tách dev/stag

Tạo hai inventory, group vars và chạy cùng `site.yml`. Chứng minh HTML/config có environment đúng. Thay đổi một biến dev không được làm thay đổi staging.

## Tài liệu chính thức

- [Inventory guide](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
- [Variable precedence](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence)
- [Best practices: directory layout](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)

