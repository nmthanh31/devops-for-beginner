# 09. Roles và cấu trúc tái sử dụng

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Đừng coi role là “thư mục để chuyển task vào”. Hãy coi role là một module có interface: input variables, resources/files do nó sở hữu, handlers và acceptance criteria.

## 1. Role là gì?

Role đóng gói một capability:

```text
Role nginx
├── nhận input: package name, ports, server name
├── tạo state: package, config, document root
├── phản ứng: reload handler
└── kiểm tra: config/service/HTTP
```

Playbook gọi role; role không nên biết environment cụ thể nếu environment có thể truyền qua variables.

## 2. Cấu trúc role

```text
roles/nginx/
├── defaults/main.yml    # input mặc định, dễ override
├── vars/main.yml        # biến nội bộ, dùng tiết chế
├── tasks/main.yml       # entrypoint tasks
├── handlers/main.yml    # change reactions
├── templates/           # Jinja2 files
├── files/               # static files
├── meta/main.yml        # dependencies/metadata
└── README.md            # contract và cách dùng
```

`defaults` có precedence thấp để caller override. `vars` có precedence cao hơn; không nên đặt mọi input vào đây vì làm role khó tái sử dụng.

## 3. Role interface

README role nên trả lời:

| Câu hỏi | Ví dụ |
|---|---|
| Input chính? | `nginx_server_name`, `nginx_listen_port` |
| File nào bị quản lý? | `/etc/nginx/conf.d/app.conf` |
| Handler nào? | `reload nginx` |
| Dependency? | `common` nếu thật sự cần |
| Acceptance? | `nginx -t`, HTTP 200 |

## 4. Gọi role từ playbook

```yaml
- name: Configure web
  hosts: web
  become: true
  roles:
    - common
    - role: nginx
      vars:
        nginx_server_name: example.test
    - app
```

Một playbook có thể dùng role chung cho dev/stag; inventory/group_vars cung cấp khác biệt.

## Lệnh cần chạy

**Git Bash/WSL — control node:**

```bash
ansible-galaxy role init roles/common
ansible-galaxy role init roles/nginx
ansible-galaxy role init roles/app
ansible-playbook -i inventories/lab/hosts.yml playbooks/site.yml --list-tasks
ansible-playbook -i inventories/lab/hosts.yml playbooks/site.yml --syntax-check
```

## Thực hành cuối chương: tách một playbook thành roles

Bắt đầu từ playbook Nginx, tách thành `common`, `nginx`, `app`. Không copy role theo môi trường. Hoàn thành khi:

- playbook chính chỉ còn hosts/vars/roles;
- mỗi role có README và defaults;
- handler/template nằm đúng role sở hữu file;
- chạy được cùng role với dev và stag.

## Tài liệu chính thức

- [Roles](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Ansible Galaxy role](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html)
- [Role directory structure](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#role-directory-structure)

