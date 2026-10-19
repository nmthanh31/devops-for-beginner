# 05. Playbook, play, task và module

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Hãy đọc playbook từ ngoài vào trong: play chọn host, task mô tả việc, module thực thi, result quyết định handler/flow tiếp theo. Chưa cần viết playbook lớn.

## 1. YAML và cấu trúc playbook

Một playbook là YAML document chứa list các play:

```yaml
- name: Configure web hosts
  hosts: web
  become: true
  gather_facts: true
  tasks:
    - name: Install Nginx
      ansible.builtin.package:
        name: nginx
        state: present
```

YAML dùng indentation để biểu diễn cấu trúc. `-` tạo phần tử list; key/value tạo mapping. Tab không hợp lệ; giá trị như `yes`, `no`, số và string cần được hiểu đúng kiểu.

## 2. Play, task và module

```text
playbook
└── play
    ├── hosts / become / vars
    ├── pre_tasks
    ├── tasks
    ├── handlers
    └── post_tasks
```

`hosts` là inventory pattern, không phải hostname Linux nhất thiết. `task` có một module chính. Tên task là interface cho người đọc và log, không chỉ là comment.

## 3. Facts, variables và register

`gather_facts` chạy `setup` để thu thập thông tin host. `vars` là dữ liệu input của play. `register` giữ result của một task để task sau đọc.

```yaml
- name: Collect and display facts
  hosts: web
  gather_facts: true
  tasks:
    - name: Show distribution
      ansible.builtin.debug:
        msg: "{{ ansible_facts['distribution'] }}"
```

Không dùng `debug` để in password/token. Result của module có thể chứa stdout/stderr, changed và failed; chỉ in field cần thiết.

## 4. `become`

```text
SSH user ── task thường
        └─ become/sudo ── package, /etc, service
```

Bật `become` ở mức nhỏ nhất có thể. Một play cần copy file `/tmp` không nhất thiết phải root; task cài package thì thường cần.

## 5. HTTP check và delegation

`uri` có thể chạy trên managed node hoặc control node. Hai lựa chọn trả lời hai câu hỏi khác nhau:

- check từ managed node: dịch vụ có truy cập được từ chính host không?
- `delegate_to: localhost`: endpoint có truy cập được từ control node không?

Phải ghi rõ vị trí thực thi để không hiểu nhầm network path.

## Cấu trúc file

```text
playbooks/
└── web.yml
```

## Thực hành cuối chương: playbook Nginx đầu tiên

Tự viết một playbook cho group `web` gồm package, enable/start service, `index.html` và HTTP check. Chạy theo checkpoint:

```bash
ansible-playbook -i inventories/lab/hosts.yml playbooks/web.yml --syntax-check
ansible-playbook -i inventories/lab/hosts.yml playbooks/web.yml --limit dev --check --diff
ansible-playbook -i inventories/lab/hosts.yml playbooks/web.yml --limit dev
```

Kết thúc khi bạn giải thích được từng dòng: target, privilege, module, input, result và check.

## Tài liệu chính thức

- [Creating a playbook](https://docs.ansible.com/ansible/latest/getting_started/get_started_playbook.html)
- [Playbook keywords](https://docs.ansible.com/ansible/latest/reference_appendices/playbooks_keywords.html)
- [Using variables](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html)

