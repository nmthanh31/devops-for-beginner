# 04. Ad-hoc commands và module

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Ad-hoc command là REPL của Ansible: dùng để quan sát hoặc thao tác nhỏ. Học module theo câu hỏi “trạng thái nào cần đạt?”, không học bằng cách ghi nhớ lệnh Linux tương đương.

## 1. Module và ad-hoc command

```text
ansible <pattern> -m <module> -a '<arguments>'
```

Module là abstraction có input, output và semantics riêng. Ví dụ `file state=directory` biết directory có tồn tại hay chưa; nó có thể báo `ok` thay vì luôn chạy `mkdir`.

## 2. Nhóm module cơ bản

| Module | Mục đích |
|---|---|
| `ping` | Kiểm tra Ansible/Python/kết nối |
| `setup` | Thu thập facts |
| `command` | Chạy executable, không qua shell |
| `shell` | Chạy shell syntax khi thật sự cần |
| `raw` | Bootstrap khi chưa có Python |
| `package` | Package abstraction |
| `service`/`systemd_service` | Service state |
| `file` | File/directory/link/state |
| `copy` | Nội dung/file tĩnh |

## 3. `command`, `shell` và `raw`

`command` không xử lý pipe, redirect hay shell expansion. Đây là mặc định an toàn hơn khi cần gọi executable.

`shell` dùng khi pipe/redirect hoặc shell builtin là một phần bản chất công việc. Nó làm việc khó idempotent hơn và tăng rủi ro injection nếu input không được kiểm soát.

`raw` gửi lệnh gần như trực tiếp qua SSH, không có đầy đủ abstraction của module. Dùng cho bootstrap rất sớm, không dùng để thay thế package/service/file module.

## 4. Module state và Linux command

```text
Linux command: “hãy chạy hành động này”
Ansible module: “hãy đưa resource về state này và báo kết quả”
```

Không phải module nào cũng idempotent tuyệt đối, nhưng module chuyên dụng thường có metadata và check mode tốt hơn shell.

## Lệnh cần chạy

**Git Bash/WSL — control node:**

```bash
ansible all -i inventories/lab/hosts.yml -m ansible.builtin.ping
ansible all -i inventories/lab/hosts.yml -m ansible.builtin.setup -a 'filter=ansible_distribution*'
ansible all -i inventories/lab/hosts.yml -m ansible.builtin.file -a 'path=/tmp/ansible-lab state=directory mode=0755'
ansible all -i inventories/lab/hosts.yml -m ansible.builtin.copy -a 'content=hello\n dest=/tmp/ansible-lab/hello.txt mode=0644'
ansible all -i inventories/lab/hosts.yml -m ansible.builtin.service -a 'name=nginx state=started enabled=true' --become
```

**Linux managed node:** kiểm tra service/container model nếu module service không phù hợp với init system của lab.

## Thực hành cuối chương: chuyển ad-hoc thành thiết kế

Thực hiện tạo directory, file, cài Nginx, start service và kiểm tra service. Với mỗi lệnh, ghi:

```text
Mục tiêu state:
Module được chọn:
Vì sao không dùng shell:
Output changed/ok:
```

Khi cùng một nhóm lệnh cần chạy lần nữa, dừng dùng ad-hoc và chuyển sang playbook ở chương 05.

## Tài liệu chính thức

- [Ansible module index](https://docs.ansible.com/ansible/latest/collections/index_module.html)
- [`command` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/command_module.html)
- [`shell` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/shell_module.html)
- [Choosing a module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/index.html)

