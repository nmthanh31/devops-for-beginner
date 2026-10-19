# 07. Variables, facts, điều kiện và vòng lặp

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Học theo ba tầng:

1. variable là dữ liệu đầu vào;
2. facts/register là dữ liệu quan sát được;
3. `when`/`loop` là cách quyết định task chạy với dữ liệu đó.

Đừng học precedence bằng cách đoán. Khi có biến trùng tên, hãy tra nguồn và kiểm tra bằng một play nhỏ.

## 1. Các nơi đặt biến

```text
play vars ──→ group_vars ──→ host_vars ──→ role defaults/vars
```

Thực tế precedence có nhiều lớp hơn sơ đồ trên. Quy tắc thiết kế quan trọng:

- `role defaults`: giá trị mặc định dễ override;
- `group_vars`: dữ liệu theo môi trường/nhóm;
- `host_vars`: ngoại lệ của một host;
- `vars`: dữ liệu nội bộ hoặc input rõ ràng;
- tránh định nghĩa cùng tên ở nhiều nơi.

## 2. Facts và register

Facts là thông tin Ansible thu thập từ host:

```yaml
ansible_facts['distribution']
ansible_facts['os_family']
ansible_facts['hostname']
ansible_facts['default_ipv4']['address']
```

`register` là result của task hiện tại, ví dụ `result.rc`, `result.stdout`, `result.changed`. Không xem register là database lâu dài.

## 3. Conditionals

```yaml
- name: Create Debian-only file
  ansible.builtin.file:
    path: /tmp/debian-only
    state: touch
  when: ansible_facts['os_family'] == 'Debian'
```

Trong `when` thường không dùng `{{ }}`. Điều kiện nên kiểm tra dữ liệu thật và fail rõ khi biến bắt buộc không có.

## 4. Loops và dữ liệu

```yaml
- name: Create users
  ansible.builtin.user:
    name: "{{ user.name }}"
    shell: "{{ user.shell }}"
    state: present
  loop: "{{ app_users }}"
  loop_control:
    loop_var: user
```

List phù hợp cho collection tuần tự; dictionary/map phù hợp khi mỗi item có key danh tính ổn định. Với loop lồng nhau, đặt `loop_var` để tránh collision.

## Cấu trúc file

```text
inventories/lab/
├── hosts.yml
├── group_vars/dev.yml
├── group_vars/stag.yml
└── host_vars/dev-web.yml
```

## Thực hành cuối chương: một playbook, hai môi trường

Đặt package list khác nhau trong `group_vars/dev.yml` và `group_vars/stag.yml`, dùng facts để chỉ tạo file trên một OS, rồi tạo nhiều user/thư mục bằng loop.

```bash
ansible-playbook -i inventories/dev/hosts.yml playbooks/variables.yml --check
ansible-playbook -i inventories/stag/hosts.yml playbooks/variables.yml --check
```

Bạn hoàn thành khi cùng một playbook tạo hành vi khác nhau do input inventory, không do copy hai playbook.

## Tài liệu chính thức

- [Variable precedence](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence)
- [Facts](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_vars_facts.html)
- [Conditionals](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html)
- [Loops](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html)

