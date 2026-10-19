# 08. Handlers, templates và file state

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Chương này nối “configuration file thay đổi” với “service cần reload”. Hãy luôn hỏi: file nào thuộc ownership của Ansible, task nào có thể thay đổi nó, và handler nào phản ứng với thay đổi đó?

## 1. Handler và change propagation

```text
template/copy changed
        ↓ notify
handler reload/restart
        ↓
service đọc configuration mới
```

Handler thường chạy cuối play và chỉ chạy khi có task notify. Nếu task `ok`, handler không chạy. Vì vậy restart nằm trong handler, không nằm trong mọi lần chạy task.

```yaml
- name: Render nginx config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/conf.d/app.conf
  notify: Reload nginx

handlers:
  - name: Reload nginx
    ansible.builtin.service:
      name: nginx
      state: reloaded
```

## 2. `template`, `copy`, `lineinfile`, `blockinfile`

| Công cụ | Mô hình ownership |
|---|---|
| `template` | Ansible sở hữu toàn bộ file, có biến/Jinja2 |
| `copy` | Nội dung tĩnh hoặc artifact |
| `lineinfile` | Một dòng có pattern rõ trong file có sẵn |
| `blockinfile` | Một block được đánh dấu do Ansible quản lý |

Không dùng `lineinfile` để quản lý cả file cấu hình phức tạp; điều đó làm ownership khó đọc.

## 3. Jinja2 template

```jinja2
<h1>{{ web_title }}</h1>
<p>Host: {{ inventory_hostname }}</p>
<p>Environment: {{ app_environment }}</p>
<p>IP: {{ ansible_facts['default_ipv4']['address'] | default('unknown') }}</p>
```

Template có thể dùng biến, filter, loop và conditional. Với giá trị có thể không tồn tại, dùng `default` có chủ đích; không dùng default để che biến bắt buộc bị thiếu.

## Cấu trúc file

```text
roles/nginx/
├── tasks/main.yml
├── handlers/main.yml
└── templates/
    ├── nginx.conf.j2
    └── index.html.j2
```

## Thực hành cuối chương: Nginx theo environment

Tạo template config và HTML để dev/stag hiển thị environment khác nhau. Khi config thay đổi, notify handler reload. Kiểm tra syntax trước khi reload:

```bash
ansible-playbook -i inventories/dev/hosts.yml playbooks/web.yml --check --diff
ansible-playbook -i inventories/dev/hosts.yml playbooks/web.yml
```

Trên **Linux managed node** có thể kiểm chứng:

```bash
sudo nginx -t
curl -fsS http://127.0.0.1/
```

## Tài liệu chính thức

- [Handlers](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html)
- [Templating with Jinja2](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_templating.html)
- [`template` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html)
- [`lineinfile` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html)

