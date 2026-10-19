# Lab 02 — Ad-hoc commands, module và idempotency

Lab 01 đã chứng minh SSH, inventory và `ansible.builtin.ping`. Lab này đi thêm một bước: dùng module để quan sát và tạo file trên managed node, sau đó chạy lại để nhìn sự khác nhau giữa `changed` và `ok`.

```text
inventory → module → managed node → changed/ok → chạy lại
```

Chưa cần viết playbook.

## 1. Mục tiêu

- Hiểu cú pháp ad-hoc command.
- Dùng `setup`, `command`, `file` và `copy`.
- Phân biệt command đọc thông tin với module quản lý state.
- Tự chứng minh một thao tác đơn giản là idempotent.

## 2. Điều kiện bắt đầu

Lab này chỉ bắt đầu khi Lab 01 đã đạt:

```bash
ssh -o BatchMode=yes -i ~/.ssh/ansible_lab_ed25519 setup@192.168.220.133 whoami
ansible lab -i inventories/lab/lesson-00.ini -m ansible.builtin.ping
```

Từ **WSL/Git Bash control node**, chuyển vào project:

```bash
cd /mnt/d/Documents/F/ansible/ansible-jun/jun
```

## 3. Công thức ad-hoc command

```bash
ansible <pattern> -i <inventory> -m <module> -a '<module arguments>'
```

Trong lab này:

```text
pattern   = lab
inventory = inventories/lab/lesson-00.ini
module    = ansible.builtin.setup / command / file / copy
```

## 4. Bước 1 — Đọc facts

Chạy trên **control node**:

```bash
ansible lab \
  -i inventories/lab/lesson-00.ini \
  -m ansible.builtin.setup \
  -a 'filter=ansible_hostname'
```

Sau đó đọc distro:

```bash
ansible lab \
  -i inventories/lab/lesson-00.ini \
  -m ansible.builtin.setup \
  -a 'filter=ansible_distribution*'
```

`setup` chủ yếu để quan sát facts. Nó không phải lệnh ICMP ping.

## 5. Bước 2 — Dùng command để quan sát

```bash
ansible lab \
  -i inventories/lab/lesson-00.ini \
  -m ansible.builtin.command \
  -a 'uname -a'
```

```bash
ansible lab \
  -i inventories/lab/lesson-00.ini \
  -m ansible.builtin.command \
  -a 'whoami'
```

`command` chạy executable trên managed node. Nó không hiểu shell pipe hoặc redirect. Ở giai đoạn này, mục tiêu là quan sát output, chưa dùng command để quản lý file.

## 6. Bước 3 — Tạo directory bằng module file

```bash
ansible lab \
  -i inventories/lab/lesson-00.ini \
  -m ansible.builtin.file \
  -a 'path=/tmp/ansible-lab-02 state=directory mode=0755'
```

Lần đầu thường có:

```text
changed: true
```

Chạy lại đúng lệnh trên:

```bash
ansible lab \
  -i inventories/lab/lesson-00.ini \
  -m ansible.builtin.file \
  -a 'path=/tmp/ansible-lab-02 state=directory mode=0755'
```

Lần hai mong đợi:

```text
changed: false
```

Đây là ví dụ idempotency: directory đã đúng state nên Ansible không tạo thay đổi mới.

## 7. Bước 4 — Copy file bằng module copy

```bash
ansible lab \
  -i inventories/lab/lesson-00.ini \
  -m ansible.builtin.copy \
  -a 'content=hello-from-lab-02 dest=/tmp/ansible-lab-02/message.txt mode=0644'
```

Chạy lại cùng lệnh lần nữa. Lần đầu thường `changed: true`, lần hai thường `changed: false` vì content và mode đã đúng.

Có thể kiểm tra nội dung bằng:

```bash
ansible lab \
  -i inventories/lab/lesson-00.ini \
  -m ansible.builtin.command \
  -a 'cat /tmp/ansible-lab-02/message.txt'
```

## 8. `command` khác `file`/`copy` thế nào?

```text
command: “chạy executable này”
file:    “directory này phải tồn tại với state/mode này”
copy:    “file này phải có content/mode này”
```

Vì `file` và `copy` quản lý state, chúng phù hợp hơn cho automation lặp lại. `command` phù hợp cho quan sát hoặc trường hợp chưa có module chuyên dụng; khi đưa vào playbook cần cân nhắc `changed_when`/`creates`.

## Acceptance criteria

- [ ] `setup` hiển thị hostname/distro của managed node.
- [ ] `command` trả về đúng user `setup`.
- [ ] Lần đầu tạo directory báo `changed`.
- [ ] Lần chạy thứ hai tạo directory báo `ok` hoặc `changed: false`.
- [ ] Lần đầu copy file báo `changed`.
- [ ] Lần chạy thứ hai copy cùng content không tạo thay đổi mới.
- [ ] Không dùng `shell` trong lab này.

## Output cần gửi để review

Gửi các output đã chạy:

```text
1. setup hostname/distro
2. command whoami
3. file directory lần 1
4. file directory lần 2
5. copy file lần 1
6. copy file lần 2
```

Không cần gửi private key hoặc password.

## Bước tiếp theo

Chưa chuyển sang playbook nếu chưa giải thích được vì sao lần đầu `changed` và lần hai `ok`. Sau lab này mới bắt đầu Lab 03 về playbook YAML.

