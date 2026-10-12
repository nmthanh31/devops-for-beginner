# Ansible Handbook thực dụng cho Junior DevOps / Platform Engineer

> Mục tiêu: từ yêu cầu cấu hình một Linux host, bạn có thể đọc hoặc viết playbook/role theo tài liệu, chạy an toàn, chứng minh idempotency, tự debug lỗi cơ bản và verify kết quả bên ngoài Ansible. Đây là đích **L3 — có thể làm theo tài liệu**, không phải thiết kế automation production quy mô lớn.

---

## 0. Cách dùng handbook này

Đừng học Ansible như một bộ từ khóa YAML. Với mỗi task, luôn trả lời bảy câu:

1. **Desired state** là gì?
2. **Current state** là gì?
3. Module kiểm tra current state bằng cách nào?
4. Điều kiện nào khiến task trả `changed`?
5. Chạy lại có còn thay đổi không?
6. Nếu task xanh, kiểm chứng service thật bằng gì?
7. Nếu fail, evidence thuộc layer nào: inventory, transport, privilege, module, OS hay application?

Thứ tự học khuyến nghị:

```text
mental model → inventory/SSH/become → play/task/module
             → variables/template/handler → role
             → idempotency/check/diff → troubleshoot → break/fix
```

### Phạm vi cần đạt

- Một control node Linux (Linux VM hoặc WSL phù hợp cho lab) điều khiển Linux managed nodes qua SSH.
- Static inventory, playbook, role, variables, facts, template và handler.
- Package, user, file, service, download, archive, HTTP check, cron, mount và firewall cơ bản.
- Ansible Vault ở mức bảo vệ secret trong repository.
- Đọc documentation bằng `ansible-doc`; cài collection bằng `ansible-galaxy`.
- Chạy lần hai không tạo thay đổi ngoài ý muốn, nhưng **không nhầm `changed=0` với ứng dụng khỏe**.

### Chủ động để sau

Dynamic inventory phức tạp, AWX/Automation Controller, Execution Environments, Molecule nâng cao, custom module/plugin, network automation chuyên sâu, multi-environment framework lớn và secret manager production. Biết chúng tồn tại là đủ ở giai đoạn này.

---

## 1. Mental model: Ansible thực sự làm gì?

Ansible là công cụ automation thường hoạt động theo mô hình **agentless push**:

```text
Control node
  ├─ ansible.cfg
  ├─ inventory + host/group vars
  ├─ playbook / role / template / file
  └─ collection + module
          │
          │ SSH, authentication, become
          ▼
Managed node
  ├─ Python/module execution
  ├─ package/file/user/service state
  └─ JSON-like result: ok/changed/failed/skipped
          │
          ▼
Independent verification
  systemctl + journalctl + ss + curl + application check
```

Ba lớp cần phân biệt:

| Lớp | Trả lời câu hỏi | Ví dụ |
|---|---|---|
| Inventory/connection | Chạy ở đâu, đăng nhập thế nào? | host, group, SSH user/key, port |
| Automation logic | Muốn host ở trạng thái nào? | package present, file đúng nội dung, service started |
| Verification | Hệ thống có phục vụ đúng không? | socket listen, HTTP 200, DB query thành công |

Terraform thường tạo infrastructure resource; Ansible thường cấu hình OS/application bên trong host. Boundary điển hình:

```text
Terraform output IP/DNS
        ↓ data handoff
Ansible inventory
        ↓ SSH/become
Host packages/config/service
        ↓ independent check
HTTP/service evidence
```

### Những object cốt lõi

- **Inventory**: danh sách host/group và connection variables.
- **Playbook**: file YAML gồm một hoặc nhiều play.
- **Play**: map một nhóm host tới tasks/roles và execution settings.
- **Task**: một hành động có tên, thường gọi đúng một module.
- **Module**: logic thực thi như `package`, `template`, `systemd_service`.
- **Role**: cấu trúc đóng gói tasks, handlers, files, templates và variables để tái sử dụng.
- **Collection**: gói phân phối content có namespace, gồm modules/plugins/roles/playbooks.
- **Plugin**: mở rộng cách Ansible kết nối, lookup, filter, inventory, callback... Module là một loại plugin đặc biệt được thực thi cho task.

### Execution flow của một playbook

```text
1. Tìm ansible.cfg
2. Parse inventory → host pattern → danh sách host mục tiêu
3. Nạp variables theo source và precedence
4. Với từng play: gather facts nếu bật
5. Với từng task: render Jinja → evaluate when/tags → gọi module
6. Module kiểm current state và chỉ đổi khi cần
7. Trả result; task changed có thể notify handler
8. Handler được notify chạy một lần ở cuối section/play
9. In recap: ok / changed / unreachable / failed / skipped / rescued / ignored
10. Verify hệ thống thật bằng evidence độc lập
```

Ý nghĩa kết quả:

- `ok`: task chạy và không cần đổi state.
- `changed`: task báo đã đổi state; không tự động có nghĩa là đổi đúng.
- `skipped`: `when`, tag hoặc điều kiện khiến task không chạy.
- `unreachable`: chưa thực thi module; thường là DNS/route/SSH/authentication.
- `failed`: đã tới bước chạy nhưng module/command/validation thất bại.
- `rescued`: lỗi được xử lý bởi `rescue`; vẫn phải xem hệ thống có đúng không.
- `ignored`: lỗi bị bỏ qua; rất dễ che incident nếu dùng tùy tiện.

---

## 2. Cài đặt và preflight

Ansible control node nên là Linux. Với máy Windows, dùng Linux VM hoặc WSL cho lab; Windows không phải native control node thông thường. Managed Linux node cần SSH và thường cần Python phù hợp với phiên bản Ansible/module.

Kiểm tra môi trường:

```bash
ansible --version
ansible-config dump --only-changed
ansible-galaxy collection list
python3 --version
ssh -V
```

Trước khi trách Ansible, thử SSH trực tiếp:

```bash
ssh -i ~/.ssh/lab_ed25519 devops@192.168.56.21
```

Sau đó mới thử connection qua Ansible:

```bash
ansible all -i inventories/lab/hosts.yml -m ansible.builtin.ping
```

`ansible.builtin.ping` không phải ICMP ping. Nó kiểm tra Ansible có thể connect, tìm Python và thực thi module đơn giản trên target hay không.

---

## 3. Cấu trúc repository mẫu

Một repo vừa đủ cho junior:

```text
ansible-lab/
├── ansible.cfg
├── requirements.yml
├── site.yml
├── inventories/
│   ├── lab/
│   │   ├── hosts.yml
│   │   ├── group_vars/
│   │   │   ├── all.yml
│   │   │   └── app.yml
│   │   └── host_vars/
│   │       └── app01.yml
│   └── prod/                 # chỉ tạo khi thật sự cần
├── roles/
│   └── app_service/
│       ├── README.md
│       ├── defaults/main.yml
│       ├── vars/main.yml
│       ├── tasks/main.yml
│       ├── tasks/install.yml
│       ├── tasks/configure.yml
│       ├── handlers/main.yml
│       ├── templates/app.conf.j2
│       ├── templates/app.service.j2
│       ├── files/banner.txt
│       ├── meta/main.yml
│       └── tests/
│           ├── inventory
│           └── test.yml
├── playbooks/
│   └── verify.yml
├── vault/
│   └── lab.yml               # encrypted; không commit password file
├── .gitignore
└── README.md
```

Nguyên tắc tổ chức:

- Inventory chứa topology và data khác nhau giữa host/environment.
- Role chứa behavior tái sử dụng.
- `defaults` là interface có thể override của role.
- Secret mã hóa riêng, không trộn secret plaintext vào `group_vars`.
- Playbook top-level càng mỏng càng tốt: chọn host, privilege, roles và validation.
- Chỉ tách file khi làm flow dễ đọc hơn; không biến một lab 10 task thành 30 file rỗng.

---

## 4. Inventory: host nào sẽ bị tác động?

### YAML inventory

`inventories/lab/hosts.yml`:

```yaml
all:
  children:
    app:
      hosts:
        app01:
          ansible_host: 192.168.56.21
        app02:
          ansible_host: 192.168.56.22
    db:
      hosts:
        db01:
          ansible_host: 192.168.56.31
```

`inventories/lab/group_vars/all.yml`:

```yaml
ansible_user: devops
ansible_become: true
ansible_python_interpreter: /usr/bin/python3
```

`inventories/lab/group_vars/app.yml`:

```yaml
app_port: 8080
app_environment: lab
```

`inventories/lab/host_vars/app01.yml`:

```yaml
app_instance_name: app01
```

Các biến connection thường gặp:

| Biến | Ý nghĩa |
|---|---|
| `ansible_host` | IP/DNS thật dùng để connect, khác inventory alias |
| `ansible_user` | SSH login user |
| `ansible_port` | SSH port |
| `ansible_ssh_private_key_file` | private key path; tránh hard-code path cá nhân trong repo chung |
| `ansible_connection` | connection plugin, thường `ssh`; `local` cho localhost |
| `ansible_python_interpreter` | Python path trên target |
| `ansible_become` | bật privilege escalation |
| `ansible_become_method` | thường `sudo` trên Linux |
| `ansible_become_user` | user sau escalation, thường `root` |

### Inventory pattern và giới hạn an toàn

```bash
ansible all --list-hosts
ansible app --list-hosts
ansible 'app:&lab' --list-hosts
ansible 'all:!db' --list-hosts
ansible-playbook site.yml --limit app01
```

Luôn dùng `--list-hosts` hoặc `ansible-inventory --graph` trước khi chạy một thay đổi có blast radius lớn. `--limit` chỉ thu hẹp host; nó không thay đổi logic task.

### Inspect inventory đã merge

```bash
ansible-inventory -i inventories/lab/hosts.yml --graph
ansible-inventory -i inventories/lab/hosts.yml --list
ansible-inventory -i inventories/lab/hosts.yml --host app01
```

Nếu variable “không như mong đợi”, `--host app01` giúp xem giá trị inventory đã nạp, nhưng vẫn phải nhớ play/role/extra vars có thể override sau đó.

---

## 5. `ansible.cfg`: hành vi mặc định của project

Ansible tìm config theo thứ tự và dùng **file đầu tiên tìm thấy**:

1. path trong environment variable `ANSIBLE_CONFIG`;
2. `ansible.cfg` ở current directory;
3. `~/.ansible.cfg`;
4. `/etc/ansible/ansible.cfg`.

Ví dụ project-local:

```ini
[defaults]
inventory = inventories/lab/hosts.yml
roles_path = roles
collections_path = collections
host_key_checking = True
retry_files_enabled = False
interpreter_python = auto_silent
forks = 10
timeout = 15

[privilege_escalation]
become = True
become_method = sudo
become_user = root
```

Không tắt `host_key_checking` theo phản xạ ở môi trường thật. Trong lab VM thường xuyên rebuild, nếu key đổi, hãy xác minh đúng VM rồi cập nhật entry `known_hosts`; đừng coi việc bỏ toàn bộ kiểm tra host key là fix production.

Debug config đang có hiệu lực:

```bash
ansible-config view
ansible-config dump --only-changed
ansible-config list
```

Phân biệt hai precedence:

- **Config behavior**: config file < command-line option < playbook keyword < variable liên quan.
- **Variable precedence**: có nhiều tầng riêng; xem mục 8.

Ví dụ `ansible_user` trong host vars là variable và có thể override `remote_user`/CLI behavior. Vì vậy khi SSH user lạ xuất hiện, đừng chỉ nhìn `ansible.cfg`.

---

## 6. Playbook, play, task và module

`site.yml` tối giản:

```yaml
---
- name: Configure application hosts
  hosts: app
  become: true
  gather_facts: true
  serial: 1

  roles:
    - role: app_service

  post_tasks:
    - name: Verify application endpoint from managed host
      ansible.builtin.uri:
        url: "http://127.0.0.1:{{ app_port }}/healthz"
        status_code: 200
      register: healthcheck
      changed_when: false
```

Giải thích:

- `name`: tên có ý nghĩa; output phải kể được flow.
- `hosts`: inventory pattern của play.
- `become`: privilege escalation cho các task trong play, trừ khi task override.
- `gather_facts`: chạy facts trước tasks.
- `serial: 1`: xử lý từng host một; hữu ích để giảm blast radius nhưng chưa tự biến deploy thành zero-downtime.
- `roles`: gọi role theo thứ tự.
- `post_tasks`: task sau roles, phù hợp cho verification ở ví dụ nhỏ.

Một task điển hình:

```yaml
- name: Ensure application package is installed
  ansible.builtin.package:
    name: nginx
    state: present
```

Ưu tiên **FQCN** (`ansible.builtin.package`) để người đọc biết module thuộc collection nào và tránh collision.

### YAML gotcha cơ bản

- Indentation bằng spaces, không dùng tab.
- Quote mode như `'0644'` để tránh parser diễn giải sai.
- Quote một scalar bắt đầu bằng Jinja: `"{{ app_port }}"`.
- Boolean nên dùng `true`/`false` nhất quán.
- List bắt đầu bằng `-`; dictionary là `key: value`.
- `name` của task mô tả desired result, không viết “Run command 1”.

### `import_*` và `include_*` ở mức cần biết

- `import_tasks`/`import_role`: static; được xử lý sớm khi parse playbook.
- `include_tasks`/`include_role`: dynamic; được quyết định ở runtime, hợp với conditional/loop cần động.

Junior không cần thuộc mọi khác biệt; chỉ cần không trộn tùy tiện. Dùng `import_tasks` để chia một role thành flow rõ ràng; dùng `include_tasks` khi thực sự cần chọn file hoặc loop lúc runtime.

---

## 7. Role: giải thích từng thư mục và file

Tạo skeleton:

```bash
ansible-galaxy role init roles/app_service
```

### `tasks/main.yml`

Entry point mặc định của role. Nó nên thể hiện flow cấp cao:

```yaml
---
- name: Install application prerequisites
  ansible.builtin.import_tasks: install.yml

- name: Configure application
  ansible.builtin.import_tasks: configure.yml

- name: Start and verify application
  ansible.builtin.import_tasks: service.yml
```

Tasks nên:

- dùng module khai báo state thay cho shell khi có module phù hợp;
- có tên rõ;
- chỉ báo changed khi thật sự đổi;
- validate config trước khi notify restart nếu module hỗ trợ;
- không chứa secret trong name/output.

### `handlers/main.yml`

Chứa actions chỉ chạy khi được `notify` bởi task có kết quả `changed`:

```yaml
---
- name: Restart app service
  ansible.builtin.systemd_service:
    name: lab-app
    state: restarted
    daemon_reload: true
```

Nếu ba template cùng notify `Restart app service`, handler thường chỉ chạy một lần ở cuối section/play. Dùng tên handler ổn định; với role lớn có thể dùng `listen` để nhiều handler nghe một topic.

Không dùng handler cho việc bắt buộc phải chạy ngay bất kể có thay đổi. Nếu task sau cần service đã restart, dùng `ansible.builtin.meta: flush_handlers` có chủ đích, không rải khắp playbook.

### `templates/`

Chứa file Jinja2 (`.j2`) được render bằng variables trên control node rồi chuyển sang target.

`templates/app.conf.j2`:

```jinja2
# Managed by Ansible. Manual changes will be overwritten.
environment = {{ app_environment }}
listen_address = {{ app_listen_address }}
port = {{ app_port }}
{% if app_log_level is defined %}
log_level = {{ app_log_level }}
{% endif %}
```

Dùng khi nội dung phụ thuộc variables. Nếu file hoàn toàn tĩnh, dùng `files/` + `copy` đơn giản hơn.

### `files/`

Chứa file tĩnh, không render Jinja. Ví dụ certificate public, script đã review, banner hoặc static config. Secret plaintext không nên để ở đây.

```yaml
- name: Install static banner
  ansible.builtin.copy:
    src: banner.txt
    dest: /etc/lab-banner.txt
    owner: root
    group: root
    mode: '0644'
```

Trong role, `src` tự được tìm trong `roles/app_service/files/` hoặc `templates/`; không cần hard-code path repo.

### `defaults/main.yml`

Defaults có precedence thấp nhất trong các variable sources phổ biến. Đây là **public interface có thể override** của role:

```yaml
---
app_user: labapp
app_group: labapp
app_port: 8080
app_listen_address: 127.0.0.1
app_environment: lab
app_packages:
  - nginx
```

Đặt ở đây những giá trị caller được phép thay đổi. Không đặt secret thật. Tên biến nên có prefix role (`app_`) để tránh collision.

### `vars/main.yml`

Role vars có precedence cao, khó override hơn. Dùng cho internal constants hoặc mapping gắn chặt với implementation:

```yaml
---
app_service_name: lab-app
app_config_path: /etc/lab-app/app.conf
```

Đừng đặt mọi thứ vào `vars`; bạn sẽ làm role khó tái sử dụng và khiến người dùng phải dùng `extra-vars` để cưỡng ép override.

### `meta/main.yml`

Metadata và dependencies của role:

```yaml
---
galaxy_info:
  author: your_name
  description: Configure the lab application service
  min_ansible_version: '2.16'
  platforms:
    - name: Ubuntu
      versions:
        - jammy
dependencies: []
```

Chỉ khai báo role dependency thật sự bắt buộc. Đừng tạo dependency ngầm lớn khiến một role nhỏ thay đổi cả host.

### `tests/`

Skeleton Galaxy thường có inventory và `test.yml`. Nó phù hợp cho smoke test thủ công đơn giản:

```yaml
---
- name: Test app_service role
  hosts: localhost
  connection: local
  become: true
  roles:
    - app_service
```

Đây chưa phải test framework đầy đủ. Với junior, quan trọng hơn là có quy trình: provision host sạch → apply → verify → apply lần hai → break/fix. Molecule/CI có thể học sau.

### `README.md`

Nên ghi: purpose, supported OS, requirements, role variables/defaults, dependencies, example playbook, verification, limitations và license nếu chia sẻ. README là contract cho người dùng role.

### Các thư mục tùy chọn nên biết

- `library/`: custom modules đi cùng role; để sau nếu module có sẵn đáp ứng được.
- `module_utils/`: code dùng chung cho custom modules.
- `lookup_plugins/`, `filter_plugins/`: plugin cục bộ. Junior nên ưu tiên collection chuẩn thay vì tự viết.

---

## 8. Variables và precedence ở mức thực dụng

### Đặt variable ở đâu?

| Nhu cầu | Vị trí hợp lý |
|---|---|
| Giá trị default cho role, cho phép caller đổi | `roles/x/defaults/main.yml` |
| Giá trị chung cho mọi host của inventory | `group_vars/all.yml` |
| Giá trị của một group | `group_vars/app.yml` |
| Ngoại lệ đúng nghĩa của một host | `host_vars/app01.yml` |
| Internal constant của role | `roles/x/vars/main.yml` |
| Giá trị tạm thời cho một lần run/deploy | `--extra-vars` có kiểm soát |
| Output của task dùng tiếp trong cùng run | `register` |
| Dữ liệu runtime từ host | facts |

### Precedence thực dụng: thấp → cao

Danh sách chính thức đầy đủ dài hơn; để làm việc hằng ngày, nhớ ladder rút gọn này:

```text
role defaults
  < inventory group vars
  < inventory host vars
  < gathered facts / cached set_facts
  < play vars / vars_prompt / vars_files
  < role vars
  < block vars
  < task vars
  < include_vars
  < registered vars / set_fact trong current run
  < role/include parameters
  < extra vars (-e)
```

Đây vẫn là ladder rút gọn: chi tiết giữa các loại `group_vars`/`host_vars`, playbook-directory và inventory-directory còn có thứ tự riêng; cached `set_fact` ở lần chạy sau có precedence thấp hơn `set_fact` đang chạy. Không nên “thắng precedence” bằng ghi nhớ toàn bộ bảng. Cách tốt hơn:

1. Một variable chỉ có một nơi sở hữu chính.
2. Role defaults là interface; environment overrides ở inventory.
3. Tránh dùng cùng tên cho internal constant và user input.
4. Dùng `ansible-inventory --host`, `debug` có chọn lọc và verbosity để tìm source.
5. `-e` có precedence rất cao; dùng nó cho input chủ ý, không dùng để vá thiết kế variable lộn xộn.

Lưu ý: command-line option như `-u` không đồng nghĩa với `--extra-vars`. Connection variable `ansible_user` có thể override behavior của option/keyword liên quan.

### Variable types và truy cập

```yaml
app_port: 8080
app_enabled: true
app_packages:
  - curl
  - nginx
app_config:
  log_level: info
  workers: 2
```

```jinja2
{{ app_port }}
{{ app_packages[0] }}
{{ app_config['log_level'] }}
{{ app_config.workers }}
```

Bracket notation an toàn hơn khi key trùng method/attribute hoặc chứa ký tự đặc biệt.

### `register` và lifetime

```yaml
- name: Read service status without changing it
  ansible.builtin.command:
    cmd: systemctl is-active lab-app
  register: app_status
  changed_when: false
  failed_when: app_status.rc not in [0, 3]

- name: Show concise status
  ansible.builtin.debug:
    msg: "status={{ app_status.stdout }} rc={{ app_status.rc }}"
```

Registered variable chỉ tồn tại trong memory của current run/play context; nó không tự trở thành persistent fact cho lần chạy sau.

---

## 9. Facts và magic variables

Facts là dữ liệu Ansible thu từ managed host khi `gather_facts: true` hoặc chạy module `setup`:

```bash
ansible app01 -m ansible.builtin.setup
ansible app01 -m ansible.builtin.setup -a 'filter=ansible_distribution*'
```

Ví dụ dùng facts:

```yaml
- name: Install package on Debian-family systems
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: true
  when: ansible_facts['os_family'] == 'Debian'
```

Facts hay dùng:

- `ansible_facts['distribution']`, `distribution_major_version`, `os_family`;
- `ansible_facts['architecture']`;
- `ansible_facts['default_ipv4']['address']` nếu tồn tại;
- `ansible_facts['mounts']`;
- `ansible_facts['service_mgr']`, `pkg_mgr`.

Magic variables không phải facts:

- `inventory_hostname`: tên alias trong inventory.
- `hostvars`: truy cập variables của host khác; dùng cẩn thận vì coupling.
- `groups`: dictionary group → hosts.
- `group_names`: groups của host hiện tại.
- `play_hosts`/`ansible_play_hosts`: hosts đang tham gia play.
- `ansible_check_mode`: có đang chạy check mode không.

Tắt `gather_facts` khi play không cần facts để giảm thời gian, nhưng đừng tắt rồi tiếp tục tham chiếu fact chưa tồn tại.

---

## 10. Conditionals, loops, retries và blocks

### Conditionals

```yaml
- name: Configure firewall only when requested
  ansible.builtin.include_tasks: firewall.yml
  when:
    - app_manage_firewall | bool
    - ansible_facts['os_family'] in ['Debian', 'RedHat']
```

Trong `when`, không bọc cả expression bằng `{{ }}`.

### Loops

```yaml
- name: Ensure required packages are installed
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop:
    - curl
    - jq
    - unzip
```

Nếu module chấp nhận list, truyền cả list thường hiệu quả hơn loop từng package:

```yaml
- name: Ensure required packages are installed
  ansible.builtin.package:
    name: "{{ app_packages }}"
    state: present
```

Loop dictionary rõ nghĩa:

```yaml
- name: Ensure service users exist
  ansible.builtin.user:
    name: "{{ account.name }}"
    groups: "{{ account.groups | default(omit) }}"
    append: true
    state: present
  loop: "{{ app_accounts }}"
  loop_control:
    loop_var: account
    label: "{{ account.name }}"
```

### Retry với `until`

```yaml
- name: Wait until local health endpoint returns 200
  ansible.builtin.uri:
    url: "http://127.0.0.1:{{ app_port }}/healthz"
    status_code: 200
  register: health
  until: health.status == 200
  retries: 10
  delay: 3
  changed_when: false
```

### `block`, `rescue`, `always`

```yaml
- name: Deploy configuration safely
  block:
    - name: Render application config
      ansible.builtin.template:
        src: app.conf.j2
        dest: /etc/lab-app/app.conf
        mode: '0640'
        validate: '/usr/local/bin/lab-app --check-config %s'
      notify: Restart app service

  rescue:
    - name: Report deployment failure
      ansible.builtin.debug:
        msg: "Configuration failed; inspect the task error and target logs"

  always:
    - name: Collect service state
      ansible.builtin.command:
        cmd: systemctl is-active lab-app
      register: final_state
      changed_when: false
      failed_when: false
```

`rescue` không phải lý do để nuốt lỗi. Nếu hệ thống không đạt desired state, playbook nên fail rõ ràng hoặc rollback có kiểm chứng.

---

## 11. Privilege escalation với `become`

Ansible thường SSH bằng user không phải root, sau đó dùng `sudo`:

```yaml
- name: Configure hosts
  hosts: app
  become: true
  become_user: root
  tasks:
    - name: Write root-owned config
      ansible.builtin.template:
        src: app.conf.j2
        dest: /etc/lab-app/app.conf
        owner: root
        group: labapp
        mode: '0640'
```

Các cách chạy:

```bash
ansible-playbook site.yml --ask-become-pass
ansible-playbook site.yml -K
```

Phân biệt:

- SSH authentication trả lời “đăng nhập host bằng ai/key nào?”.
- `become` trả lời “sau khi vào host, task chạy với privilege nào?”.

Lỗi thường gặp:

- `Permission denied (publickey)` → SSH user/key, chưa liên quan sudo.
- `Missing sudo password` → SSH đã thành công, become cần password.
- `user is not in the sudoers file` → policy trên target.
- File tạo sai owner dù play xanh → task không become hoặc module args sai.

Không chạy toàn play bằng root nếu chỉ một vài task cần quyền cao; có thể đặt `become: true` ở block/task cần thiết để giảm phạm vi.

---

## 12. Handlers và change propagation

Flow đúng:

```text
template/copy thay đổi config
        ↓ result.changed = true
notify handler
        ↓ cuối play/section
restart/reload đúng một lần
        ↓
verify service + socket + request
```

Ví dụ:

```yaml
- name: Render systemd unit
  ansible.builtin.template:
    src: app.service.j2
    dest: /etc/systemd/system/lab-app.service
    owner: root
    group: root
    mode: '0644'
  notify:
    - Reload systemd
    - Restart app service
```

```yaml
handlers:
  - name: Reload systemd
    ansible.builtin.systemd_service:
      daemon_reload: true

  - name: Restart app service
    ansible.builtin.systemd_service:
      name: lab-app
      state: restarted
```

Pitfalls:

- Task dùng `command` luôn báo changed → handler restart mỗi run.
- Task cấu hình không notify → file đổi nhưng process vẫn dùng config cũ.
- Handler restart trước khi config validate → outage do syntax sai.
- Handler bị notify nhưng task sau verify chạy trước handler → cần `flush_handlers` có chủ đích.
- Nhiều handler cùng tên có thể gây shadowing/confusion; đặt tên rõ hoặc dùng `listen`.

---

## 13. Templates và Jinja2 đủ dùng

### Filters phổ biến

```jinja2
{{ app_port | int }}
{{ app_enabled | bool }}
{{ app_owner | default('root') }}
{{ app_hosts | join(',') }}
{{ app_config | to_nice_yaml }}
{{ secret_value | mandatory }}
```

`default` có thể che việc thiếu variable bắt buộc. Chỉ default khi thực sự có default hợp lệ; với input bắt buộc, dùng `mandatory` hoặc `assert`.

### Loop và condition trong template

```jinja2
{% for backend in app_backends %}
server {{ backend.name }} {{ backend.address }}:{{ backend.port }};
{% endfor %}

{% if app_tls_enabled %}
tls = true
certificate = {{ app_tls_cert_path }}
{% endif %}
```

### Whitespace và validation

Jinja whitespace sai có thể tạo config lỗi dù template render thành công. Luôn xem rendered file và dùng `validate` nếu module/tool hỗ trợ:

```yaml
- name: Render sudoers fragment safely
  ansible.builtin.template:
    src: labapp.sudoers.j2
    dest: /etc/sudoers.d/labapp
    mode: '0440'
    validate: '/usr/sbin/visudo -cf %s'
```

Với secret template:

```yaml
- name: Render secret config without exposing diff/log output
  ansible.builtin.template:
    src: secret.conf.j2
    dest: /etc/lab-app/secret.conf
    owner: root
    group: labapp
    mode: '0640'
  no_log: true
  diff: false
  notify: Restart app service
```

`no_log` giảm rò rỉ qua output nhưng không sửa quyền file, history, backup hay việc secret đã từng commit.

---

## 14. Idempotency: chạy lại không tạo drift ngoài ý muốn

Một playbook idempotent đưa host tới desired state và lần chạy sau, nếu input/reality không đổi, không tạo change tiếp.

### Chứng minh tối thiểu

```bash
ansible-playbook site.yml --limit app01
ansible-playbook site.yml --limit app01
```

Kỳ vọng lần hai: `changed=0`, sau đó vẫn kiểm:

```bash
ansible app01 -b -m ansible.builtin.command -a 'systemctl is-active lab-app'
ansible app01 -b -m ansible.builtin.command -a 'ss -lnt'
curl -fsS http://192.168.56.21:8080/healthz
```

`changed=0` chỉ chứng minh Ansible không thấy cần thay đổi theo logic đã viết. Nó không chứng minh desired state đầy đủ, endpoint đúng, dependency khỏe hay người dùng truy cập được.

### Nguồn gây non-idempotency

- `shell: echo ... >> file` nối thêm mỗi lần.
- Download file không có checksum/version rõ.
- Template chứa timestamp/random value.
- `state: restarted` ở task thường thay vì handler.
- `command`/`shell` thiếu `creates`, `removes`, `changed_when`.
- `state: latest` khiến kết quả phụ thuộc repository tại thời điểm chạy.
- API task luôn POST tạo object mới thay vì kiểm object đã tồn tại.

### Làm command có guard

```yaml
- name: Initialize database only once
  ansible.builtin.command:
    cmd: /usr/local/bin/lab-app init-db
    creates: /var/lib/lab-app/.initialized
```

`creates` chỉ là guard filesystem; phải chắc marker thực sự đại diện cho state đúng. Nếu có module chuyên dụng, ưu tiên module đó.

---

## 15. Check mode và diff mode

```bash
ansible-playbook site.yml --check
ansible-playbook site.yml --check --diff --limit app01
```

- **Check mode**: module hỗ trợ sẽ dự đoán change mà không áp dụng.
- **Diff mode**: module hỗ trợ sẽ hiển thị before/after, đặc biệt hữu ích với file/template.

Giới hạn:

- Check mode là simulation, không phải transaction hay proof an toàn.
- Module không hỗ trợ có thể skip/không báo đầy đủ.
- Task sau phụ thuộc registered output từ task trước có thể không dự đoán đúng.
- API/external side effect và custom command có thể có semantics khác.
- `--diff` có thể lộ secret; dùng `diff: false`/`no_log: true` ở task nhạy cảm.

Workflow an toàn cho thay đổi nhỏ:

```text
syntax-check → list-hosts/tasks/tags → check+diff một host
→ review diff → apply một host → verify → mở rộng phạm vi
```

---

## 16. Vault và secret basics

Ansible Vault mã hóa data/file at rest trong repo; nó không phải full secret manager và không tự giải quyết rotation, access audit hay runtime secret distribution.

Các lệnh cơ bản:

```bash
ansible-vault create vault/lab.yml
ansible-vault edit vault/lab.yml
ansible-vault view vault/lab.yml
ansible-vault encrypt group_vars/app/secrets.yml
ansible-vault decrypt path/to/file.yml
ansible-vault rekey vault/lab.yml
```

Chạy playbook:

```bash
ansible-playbook site.yml --ask-vault-pass
ansible-playbook site.yml --vault-password-file /secure/path/lab-vault-pass
```

Rules:

- Không commit vault password file, private key, token hoặc plaintext secret.
- Vault-encrypted content có thể commit nếu policy cho phép, nhưng ai có vault password sẽ đọc được.
- Tách variable name không nhạy cảm và encrypted value giúp review dễ hơn.
- Dùng file permission chặt trên target (`0600`/`0640`) và tránh log/diff secret.
- Nếu secret từng commit plaintext, xóa ở commit mới là chưa đủ: rotate/revoke secret và xử lý Git history theo quy trình team.
- Production nên cân nhắc external secret manager và short-lived identity; không biến Vault thành lý do giữ credential lâu dài.

---

## 17. Collections và plugins ở mức cần biết

FQCN có dạng:

```text
namespace.collection.module
ansible.builtin.copy
community.general.ufw
ansible.posix.mount
```

`requirements.yml`:

```yaml
---
collections:
  - name: ansible.posix
    version: '>=1.5.0,<2.0.0'
  - name: community.general
    version: '>=8.0.0,<10.0.0'
```

Cài dependency:

```bash
ansible-galaxy collection install -r requirements.yml
ansible-galaxy collection list
ansible-doc -t module ansible.posix.mount
```

Trong repo team/CI, pin range hoặc exact version theo policy và test trước upgrade. `ansible-core` chỉ mang built-in content; nhiều module community nằm ở collections khác.

Plugin bạn chỉ cần nhận diện:

- connection plugin: cách nối target (`ssh`, `local`...);
- become plugin: cách nâng quyền (`sudo`...);
- inventory plugin: tạo inventory từ source;
- lookup plugin: đọc data từ control node/external source;
- filter plugin: biến đổi data trong Jinja;
- callback plugin: format/đưa event output.

Đừng cài collection chỉ vì thấy tên module. Kiểm source, version compatibility, documentation, maintenance và quyền mà module sẽ dùng.

---

## 18. Các module quan trọng và cách chọn

### 18.1 Package: `package`, `apt`, `dnf`, `yum`

`package` là abstraction dùng package manager phù hợp:

```yaml
- name: Ensure baseline packages are installed
  ansible.builtin.package:
    name:
      - curl
      - jq
    state: present
```

Dùng module OS-specific khi cần option riêng:

```yaml
- name: Refresh APT cache and install nginx
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: true
    cache_valid_time: 3600
```

```yaml
- name: Install nginx on modern RHEL-family systems
  ansible.builtin.dnf:
    name: nginx
    state: present
```

`yum` vẫn gặp ở codebase/host cũ; trên hệ mới ưu tiên module phù hợp documentation/platform. `state: present` reproducible hơn `latest`; nếu cần patch/latest, đó phải là quyết định maintenance có review.

### 18.2 Service: `service`, `systemd_service`

```yaml
- name: Ensure nginx is enabled and running
  ansible.builtin.service:
    name: nginx
    enabled: true
    state: started
```

```yaml
- name: Reload unit files and start lab app
  ansible.builtin.systemd_service:
    name: lab-app
    daemon_reload: true
    enabled: true
    state: started
```

`service` là abstraction; `systemd_service` dùng khi cần semantics systemd như `daemon_reload`, `masked`. Không dùng `state: restarted` mỗi run trừ khi restart luôn luôn là yêu cầu; thường restart nằm trong handler.

### 18.3 File content/state: `file`, `copy`, `template`

```yaml
- name: Ensure config directory exists
  ansible.builtin.file:
    path: /etc/lab-app
    state: directory
    owner: root
    group: labapp
    mode: '0750'
```

```yaml
- name: Copy static file
  ansible.builtin.copy:
    src: banner.txt
    dest: /etc/lab-app/banner.txt
    owner: root
    group: root
    mode: '0644'
    backup: true
```

```yaml
- name: Render variable-based config
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/lab-app/app.conf
    owner: root
    group: labapp
    mode: '0640'
  notify: Restart app service
```

`file` không ghi nội dung file. `copy` dùng static content; `template` dùng Jinja variables.

### 18.4 Identity: `user`, `group`

```yaml
- name: Ensure application group exists
  ansible.builtin.group:
    name: labapp
    system: true
    state: present

- name: Ensure application user exists
  ansible.builtin.user:
    name: labapp
    group: labapp
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

Cẩn thận với `groups`: nếu đặt supplementary groups mà quên `append: true`, có thể loại user khỏi group khác. Không đặt plaintext password.

### 18.5 `command` và `shell`

```yaml
- name: Run executable without a shell
  ansible.builtin.command:
    cmd: /usr/local/bin/lab-app migrate
  register: migration
  changed_when: "'applied 0 migrations' not in migration.stdout"
```

```yaml
- name: Run pipeline that genuinely requires shell features
  ansible.builtin.shell:
    cmd: set -o pipefail && journalctl -u lab-app --since today | grep -q ERROR
    executable: /bin/bash
  register: error_scan
  changed_when: false
  failed_when: error_scan.rc not in [0, 1]
```

Chọn `command` mặc định vì không qua shell. Chỉ dùng `shell` khi cần pipe, redirect, wildcard, shell variable hoặc compound expression. Không đưa untrusted variable vào shell command. Cả hai thường cần `changed_when`, `creates` hoặc `removes` để có semantics idempotent.

### 18.6 Download/archive: `get_url`, `unarchive`

```yaml
- name: Download release archive with integrity check
  ansible.builtin.get_url:
    url: "https://example.invalid/lab-app-{{ app_version }}.tar.gz"
    dest: "/var/tmp/lab-app-{{ app_version }}.tar.gz"
    checksum: "sha256:{{ app_archive_sha256 }}"
    mode: '0644'

- name: Extract release once
  ansible.builtin.unarchive:
    src: "/var/tmp/lab-app-{{ app_version }}.tar.gz"
    dest: /opt/lab-app
    remote_src: true
    creates: "/opt/lab-app/releases/{{ app_version }}"
```

Checksum chứng minh integrity của artifact mong đợi; HTTPS một mình không pin content/version.

### 18.7 Chỉnh file có sẵn: `lineinfile`, `blockinfile`

```yaml
- name: Set one well-defined key
  ansible.builtin.lineinfile:
    path: /etc/example.conf
    regexp: '^log_level='
    line: 'log_level=info'
    backup: true
```

```yaml
- name: Manage one owned block
  ansible.builtin.blockinfile:
    path: /etc/hosts
    marker: '# {mark} ANSIBLE MANAGED LAB'
    block: |
      192.168.56.21 app01
      192.168.56.22 app02
```

Dùng khi chỉ sở hữu một dòng/block trong file do hệ khác quản lý. Nếu Ansible sở hữu toàn bộ file, template thường rõ và test được hơn. Regex sai có thể nhân đôi dòng; test run thứ hai.

### 18.8 Git: `git`

```yaml
- name: Check out an immutable application revision
  ansible.builtin.git:
    repo: https://github.com/example/lab-app.git
    dest: /opt/lab-app/src
    version: "{{ app_git_commit }}"
    update: true
```

Pin tag/commit thay vì `main` nếu cần reproducibility. Deploy source bằng Git trên host có thể hợp lab nhưng production thường build immutable artifact/image ở CI.

### 18.9 HTTP/API: `uri`

```yaml
- name: Verify health endpoint
  ansible.builtin.uri:
    url: "http://127.0.0.1:{{ app_port }}/healthz"
    method: GET
    status_code: 200
    return_content: true
  register: health
  changed_when: false

- name: Assert health response
  ansible.builtin.assert:
    that:
      - health.json.status == 'ok'
    fail_msg: "Application endpoint returned 200 but payload is not healthy"
```

Với API mutation, hiểu idempotency của HTTP method/API; một POST create mỗi run có thể tạo duplicate.

### 18.10 Debug/validation/data: `debug`, `assert`, `set_fact`

```yaml
- name: Validate required inputs
  ansible.builtin.assert:
    that:
      - app_port | int > 0
      - app_port | int < 65536
      - app_environment in ['lab', 'staging', 'prod']
    fail_msg: "Invalid app role inputs"
```

```yaml
- name: Derive endpoint for this run
  ansible.builtin.set_fact:
    app_health_url: "http://127.0.0.1:{{ app_port }}/healthz"
```

`debug` không nên dump toàn bộ `hostvars`/secret. `set_fact` có precedence/lifetime đặc thù và có thể làm dataflow khó theo dõi; ưu tiên normal vars/defaults cho giá trị tĩnh.

### 18.11 Chờ dependency: `wait_for`

```yaml
- name: Wait for application port
  ansible.builtin.wait_for:
    host: 127.0.0.1
    port: "{{ app_port }}"
    state: started
    timeout: 30
```

Port mở chỉ chứng minh listener/TCP, không chứng minh HTTP/business health; theo sau bằng `uri` hoặc protocol check phù hợp.

### 18.12 Scheduled job: `cron`

```yaml
- name: Schedule daily cleanup
  ansible.builtin.cron:
    name: lab-app cleanup
    user: labapp
    minute: '15'
    hour: '2'
    job: '/usr/local/bin/lab-app cleanup >> /var/log/lab-app-cleanup.log 2>&1'
    state: present
```

`name` là identifier giúp module quản đúng entry. Verify timezone, environment tối giản của cron, permission và log rotation.

### 18.13 Mount: `ansible.posix.mount`

```yaml
- name: Ensure data filesystem is mounted and persistent
  ansible.posix.mount:
    path: /srv/lab-data
    src: /dev/disk/by-uuid/REPLACE-ME
    fstype: ext4
    opts: defaults
    state: mounted
```

Mount sai có thể gây mất truy cập dữ liệu hoặc boot issue. Xác minh device/UUID, filesystem, mountpoint và backup trước thay đổi. Phân biệt `mounted`, `present`, `unmounted`, `absent` trong docs.

### 18.14 Firewall: `firewalld`, `ufw`

RHEL-family với firewalld:

```yaml
- name: Allow application port in firewalld
  ansible.posix.firewalld:
    port: "{{ app_port }}/tcp"
    permanent: true
    immediate: true
    state: enabled
```

Ubuntu với UFW (module thường thuộc `community.general`):

```yaml
- name: Allow app traffic from lab subnet
  community.general.ufw:
    rule: allow
    src: 192.168.56.0/24
    port: "{{ app_port }}"
    proto: tcp
```

Firewall automation có thể tự khóa SSH. Với host remote: xác nhận console/out-of-band recovery, allow SSH đúng source trước, `--limit` một host, và verify connection sau change.

---

## 19. Các câu lệnh quan trọng

### `ansible`: ad-hoc investigation/thao tác nhỏ

```bash
ansible all --list-hosts
ansible app -m ansible.builtin.ping
ansible app01 -m ansible.builtin.setup -a 'filter=ansible_distribution*'
ansible app -b -m ansible.builtin.package -a 'name=curl state=present' --check
ansible app01 -b -m ansible.builtin.command -a 'systemctl is-active lab-app'
```

Ad-hoc phù hợp cho discovery, one-off bounded operation và incident check; thay đổi cần lặp lại nên đi vào playbook/role.

### `ansible-playbook`

```bash
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml --list-hosts
ansible-playbook site.yml --list-tasks
ansible-playbook site.yml --list-tags
ansible-playbook site.yml --check --diff --limit app01
ansible-playbook site.yml --limit app01
ansible-playbook site.yml --tags config
ansible-playbook site.yml --skip-tags packages
ansible-playbook site.yml --start-at-task 'Render application config'
ansible-playbook site.yml -e '@release.yml'
ansible-playbook site.yml -v
ansible-playbook site.yml -vvv
```

Verbosity tăng dần; `-vvv` thường đủ để xem connection/task details. Không đăng log verbose công khai vì có thể chứa path, host, argument hoặc secret.

### `ansible-inventory`

```bash
ansible-inventory --graph
ansible-inventory --list
ansible-inventory --host app01
ansible-inventory -i inventories/lab/hosts.yml --graph
```

### `ansible-galaxy`

```bash
ansible-galaxy role init roles/app_service
ansible-galaxy collection install -r requirements.yml
ansible-galaxy collection list
ansible-galaxy role list
```

Không dùng `--force` với `role init` trong thư mục đã có nội dung nếu chưa hiểu nó sẽ ghi đè gì.

### `ansible-doc`

```bash
ansible-doc ansible.builtin.template
ansible-doc -s ansible.builtin.template
ansible-doc -t module -l
ansible-doc -t lookup -l
ansible-doc -t inventory -l
```

Khi chọn module, đọc ít nhất: synopsis, parameters, examples, attributes (`check_mode`, `diff_mode`) và return values.

### `ansible-config` và `ansible-vault`

```bash
ansible-config dump --only-changed
ansible-config view
ansible-vault view vault/lab.yml
ansible-vault edit vault/lab.yml
```

---

## 20. Tags: hữu ích nhưng có thể tạo partial state

```yaml
- name: Install packages
  ansible.builtin.import_tasks: install.yml
  tags: [packages]

- name: Configure application
  ansible.builtin.import_tasks: configure.yml
  tags: [config]
```

Tags giúp chạy scoped tasks, nhưng `--tags config` có thể bỏ prerequisite package/user/directory. Vì vậy:

- Mỗi tag path cần được test.
- Đừng coi tag như dependency engine.
- Dùng tags cho operations rõ như `config`, `verify`, `never`/manual maintenance, không gắn tag tùy tiện vào mọi task.
- Khi troubleshoot, kiểm command đã dùng tag/skip-tag gì.

---

## 21. Troubleshooting workflow: evidence trước, thay đổi sau

### Cây chẩn đoán tổng quát

```text
Đúng host không?
  └─ ansible-inventory --graph/--host, --list-hosts, --limit
        ↓
Reachable không?
  └─ DNS/IP/route → TCP 22 → ssh trực tiếp → ansible ping
        ↓
Authentication đúng không?
  └─ user/key/known_hosts/port/ssh config
        ↓
Become đúng không?
  └─ sudo policy/password/become_user
        ↓
Variable/template đúng không?
  └─ undefined/source/type/rendered file/diff
        ↓
Module/task đúng semantics không?
  └─ ansible-doc, args, rc/stdout/stderr, check support
        ↓
OS state đúng không?
  └─ package/file owner+mode/service/process/socket/journal
        ↓
Application path đúng không?
  └─ DNS/TCP/TLS/HTTP/auth/dependency/data
```

### `UNREACHABLE`

1. `ansible-playbook ... --list-hosts` — có chọn đúng host không?
2. `ansible-inventory --host app01` — IP/user/port/key path có đúng không?
3. `ip route get <ip>`, `getent hosts <name>`, `nc -vz <host> 22`.
4. SSH trực tiếp với cùng user/key và `-vvv` nếu cần.
5. Xử lý host key mismatch chỉ sau khi xác minh host bị rebuild hợp lệ.
6. `ansible app01 -m ping -vvv` để xem Ansible dùng connection nào.

### `FAILED` ở become

1. Xác nhận SSH login đã thành công.
2. Trên target: `sudo -l` cho login user.
3. Kiểm `become`, `become_method`, `become_user` và password expectation.
4. Thu hẹp tới một command an toàn: `ansible app01 -b -m command -a 'id'`.

### Undefined/wrong variable

1. Ghi chính xác tên và host lỗi.
2. `ansible-inventory --host <host>`.
3. Kiểm `group_vars`/`host_vars` nằm cạnh đúng inventory/playbook.
4. Kiểm typo, YAML type, variable prefix và extra-vars.
5. Dùng `assert` tại role entry để fail sớm.
6. Không dùng `default(...)` chỉ để làm lỗi biến mất nếu variable là bắt buộc.

### Task xanh nhưng service hỏng

```text
rendered config → unit file → daemon reload → service state
→ process owner/env/cwd → socket bind → local request
→ remote request/firewall → dependency → logs
```

Evidence trên host:

```bash
systemctl status lab-app --no-pager
journalctl -u lab-app -n 100 --no-pager
systemctl cat lab-app
ss -lntp
curl -v http://127.0.0.1:8080/healthz
namei -l /etc/lab-app/app.conf
```

### Handler không chạy

- Task notify có thật sự `changed` không?
- Tên `notify` có match handler/listen không?
- Handler đã được load chưa?
- Play fail trước khi tới handler không?
- Task verify chạy trước handler không?
- `changed_when` có ép sai thành `false` không?

### Luôn changed ở lần hai

1. Tìm task changed trong output; chạy `--limit` một host và `--diff`.
2. So before/after: timestamp, order, whitespace, generated value hay API response?
3. Kiểm command/shell, `state: latest/restarted`, download, template dynamic data.
4. Sửa semantics, không ép `changed_when: false` chỉ để recap đẹp.
5. Chạy lại hai lần và verify service.

### Mẫu incident note

```markdown
## Symptom / impact
## Last known good / recent change
## Hypothesis đầu tiên
## Evidence đã thu
## Root cause và layer sở hữu
## Minimal fix / rollback
## Verification độc lập
## Prevention hoặc test bổ sung
```

---

## 22. Best practices và anti-patterns

### Best practices

- Đặt task name mô tả desired state và object.
- Dùng FQCN và pin dependency collection phù hợp.
- Bắt đầu bằng một host: `--limit`, review host list, check/diff rồi apply.
- Dùng module chuyên dụng trước `command`, dùng `command` trước `shell`.
- Tách data khỏi behavior: inventory variables vs role tasks.
- Role defaults là public inputs; prefix variable theo role.
- Validate input bằng `assert`, config bằng tool-specific validation.
- Template/copy thay đổi thì notify handler; restart đúng lúc.
- Owner/group/mode explicit cho file nhạy cảm.
- Download có version/checksum.
- Secret encrypted, output/diff được kiểm soát, quyền target đúng.
- Chạy từ clean host/snapshot, chạy lần hai, rồi verify service/socket/request.
- Commit evidence đã redacted: two recaps, HTTP check, incident notes.
- Ghi supported OS/version và known limitations.

### Anti-patterns và vì sao nguy hiểm

| Anti-pattern | Vấn đề | Thay bằng |
|---|---|---|
| `shell: apt install ...` | khó idempotent, phụ thuộc shell | `apt`/`package` |
| `chmod -R 777` | che ownership/root cause, mở quyền quá rộng | owner/group/mode tối thiểu |
| `ignore_errors: true` khắp nơi | play xanh giả, mất failure boundary | `failed_when`, `block/rescue`, fix cause |
| `changed_when: false` để recap đẹp | che drift/non-idempotency | sửa detection/guard/module |
| `state: latest` mọi package | upgrade không kiểm soát | pin/present + maintenance policy |
| Restart service mỗi run | downtime, che config change | handler |
| Secret trong vars plaintext/log | credential leak | Vault/external manager + `no_log` |
| Dump `hostvars` bằng debug | lộ secret và noise | debug field cần thiết |
| Tắt host key checking toàn cục | mất xác minh server | quản lý known_hosts đúng |
| Một role làm mọi thứ | blast radius/coupling khó test | boundary theo responsibility |
| Copy cả config bằng `lineinfile` nhiều lần | regex/order khó kiểm soát | template nếu sở hữu toàn file |
| Tin recap xanh là healthy | không test runtime/user path | independent verification |
| Chạy toàn fleet lần đầu | blast radius lớn | one host → batch → fleet |

---

## 23. Khung role end-to-end: service nhỏ

Ví dụ này tập trung vào control flow `input → state → handler → verification`. Để chạy thật, bạn phải bổ sung bước cài `lab-app` binary/script và nội dung hai template theo ứng dụng của lab; không nên copy rồi giả định một executable chưa tồn tại.

`roles/app_service/defaults/main.yml`:

```yaml
---
app_user: labapp
app_group: labapp
app_port: 8080
app_listen_address: 127.0.0.1
app_environment: lab
```

`roles/app_service/tasks/main.yml`:

```yaml
---
- name: Validate app_service inputs
  ansible.builtin.assert:
    that:
      - app_port | int > 0
      - app_port | int < 65536
      - app_environment in ['lab', 'staging', 'prod']

- name: Ensure application group exists
  ansible.builtin.group:
    name: "{{ app_group }}"
    system: true
    state: present

- name: Ensure application user exists
  ansible.builtin.user:
    name: "{{ app_user }}"
    group: "{{ app_group }}"
    system: true
    create_home: false
    shell: /usr/sbin/nologin
    state: present

- name: Ensure application directory exists
  ansible.builtin.file:
    path: /etc/lab-app
    state: directory
    owner: root
    group: "{{ app_group }}"
    mode: '0750'

- name: Render application config
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/lab-app/app.conf
    owner: root
    group: "{{ app_group }}"
    mode: '0640'
  notify: Restart app service

- name: Render systemd unit
  ansible.builtin.template:
    src: app.service.j2
    dest: /etc/systemd/system/lab-app.service
    owner: root
    group: root
    mode: '0644'
  notify:
    - Reload systemd
    - Restart app service

- name: Ensure application is enabled and started
  ansible.builtin.systemd_service:
    name: lab-app
    enabled: true
    state: started

- name: Apply pending service changes before verification
  ansible.builtin.meta: flush_handlers

- name: Wait for application port
  ansible.builtin.wait_for:
    host: "{{ app_listen_address }}"
    port: "{{ app_port }}"
    timeout: 30

- name: Verify application endpoint
  ansible.builtin.uri:
    url: "http://{{ app_listen_address }}:{{ app_port }}/healthz"
    status_code: 200
  register: app_health
  retries: 5
  delay: 2
  until: app_health.status == 200
  changed_when: false
```

`roles/app_service/handlers/main.yml`:

```yaml
---
- name: Reload systemd
  ansible.builtin.systemd_service:
    daemon_reload: true

- name: Restart app service
  ansible.builtin.systemd_service:
    name: lab-app
    state: restarted
```

Điểm cần tự giải thích:

- Vì sao user/group tạo trước directory?
- Vì sao `template` notify nhưng `systemd_service state=started` không restart mỗi run?
- Vì sao phải flush handler trước health check?
- `wait_for` và `uri` chứng minh hai điều khác nhau thế nào?
- Điều gì trong role vẫn phụ thuộc app binary có sẵn và cần được bổ sung?

---

## 24. Lab và break/fix exercises

Mỗi lab phải lưu: hypothesis, command/evidence, minimal fix, run thứ hai và verification. Làm trong VM/snapshot lab; không phá máy công ty hoặc production.

### Lab 1 — Inventory → SSH → become

**Build:** một VM Ubuntu, user `devops`, SSH key, sudo phù hợp. Viết inventory alias `app01`.

**Break:**

1. `ansible_host` sai.
2. `ansible_user` sai.
3. key path sai hoặc permission sai.
4. sudo policy thiếu.

**PASS:** nhìn `unreachable` vs `failed` và xác định đúng 4/4 layer trước khi sửa; `ping` và `become command id` thành công.

### Lab 2 — Package, user, file, service

**Build:** role tạo system user, directory, static script/systemd service, start và enable service.

**Break:** owner/mode sai; `ExecStart` sai; quên `daemon_reload`; port đã bị chiếm.

**PASS:** chạy từ snapshot sạch, service active, đúng process owner, đúng socket; lần hai `changed=0`.

### Lab 3 — Template → handler → verification

**Build:** config có port/log level; đổi một variable phải render config, notify đúng một restart và health check xanh.

**Break:** typo variable; template syntax sai; notify sai tên; config đổi nhưng handler không chạy; bind `127.0.0.1` trong khi test remote.

**PASS:** sửa 4/5 lỗi; giải thích rendered file khác template source thế nào; chứng minh handler không chạy khi không đổi.

### Lab 4 — Idempotency hunt

Đưa vào role bốn lỗi:

- timestamp trong template;
- `shell: echo line >> file`;
- service `restarted` trong normal task;
- download/update tracking `latest`.

**PASS:** dùng second run + diff xác định từng nguồn; sửa semantics thay vì che `changed`; second run `changed=0` và HTTP vẫn OK.

### Lab 5 — Variables và precedence

Đặt `app_port` khác nhau ở role defaults, group vars, host vars, play vars và extra vars. Trước mỗi run, dự đoán giá trị thắng rồi verify rendered config.

**PASS:** đúng ít nhất 4/5 case; dọn lại để mỗi giá trị có một owner hợp lý; giải thích vì sao `-e` không nên là cách vá thường trực.

### Lab 6 — Check/diff và secret hygiene

**Build:** một normal template và một secret template từ Vault.

**Break:** để diff lộ secret giả; mode `0644`; vault password file bị Git track.

**PASS:** `--check --diff --limit app01` hữu dụng mà không lộ secret; file secret `0640`/`0600`; password file ignored; biết rằng secret giả bị lộ vẫn phải rotate trong tình huống thật.

### Lab 7 — Download/release

**Build:** tải artifact versioned có checksum, extract vào release directory, symlink/current hoặc config phù hợp, restart khi version đổi.

**Break:** checksum sai; URL 404; archive hỏng; permission execute thiếu.

**PASS:** phân biệt network/HTTP/integrity/archive/permission; rerun không download/extract/restart vô ích.

### Lab 8 — Firewall an toàn

**Build:** mở app port chỉ từ lab subnet, giữ SSH access.

**Safety:** snapshot/console trước khi đổi; `--limit app01`; ghi rollback.

**Break:** app listen đúng nhưng firewall drop; rule đúng port sai source; rule runtime có nhưng permanent thiếu (hoặc ngược lại).

**PASS:** dùng socket + local request + remote TCP/request để định vị layer; không tự khóa SSH.

### Lab 9 — Green playbook, broken app

Tạo ba case không làm playbook fail ngay:

1. service active nhưng bind localhost;
2. TCP mở nhưng `/healthz` trả 500;
3. app khỏe local nhưng remote bị firewall chặn.

**PASS:** không kết luận từ recap; trace `service → process → socket → local HTTP → remote path`; thêm verification phù hợp mà không hard-code hack.

### Lab 10 — Cold rebuild

Từ VM snapshot sạch hoặc host mới:

```text
inventory → connectivity → apply role → handler → service/socket/HTTP
→ second run changed=0 → induced fault → diagnose → restore
```

**PASS:** README đủ để một người khác chạy; không sửa task theo từng host; không cần secret chỉ tồn tại trong đầu; có hai recaps và evidence HTTP.

---

## 25. Checklist PASS để đạt L3

Chỉ đánh dấu PASS khi có evidence, không đánh dấu vì đã xem video/đọc hết file.

### Mental model

- [ ] Vẽ và giải thích được `control node → inventory → SSH/become → module → result → handler → verification`.
- [ ] Phân biệt inventory, playbook, play, task, module, role, collection và plugin.
- [ ] Phân biệt Terraform provision infrastructure với Ansible configure host.
- [ ] Giải thích được `ok`, `changed`, `skipped`, `unreachable`, `failed`.

### Inventory/config/variables

- [ ] Tự viết YAML inventory có group, host alias, group vars và host vars.
- [ ] Dùng `ansible-inventory --graph/--host` để chứng minh target và merged inventory data.
- [ ] Biết Ansible đang dùng `ansible.cfg` nào và xem changed config.
- [ ] Chọn đúng nơi đặt role default, group override, host exception và runtime input.
- [ ] Dự đoán được precedence trong các case thực dụng, đặc biệt `-e`.

### Playbook/role

- [ ] Tự viết playbook gọi một role và đọc được flow từ task names.
- [ ] Giải thích được từng thư mục `tasks`, `handlers`, `templates`, `files`, `defaults`, `vars`, `meta`, `tests`.
- [ ] Dùng condition, loop, register, assert, tag và facts trong đúng ngữ cảnh.
- [ ] Dùng `become` đúng boundary, không nhầm SSH auth với sudo.
- [ ] Template thay đổi mới notify handler; config được validate nếu có thể.

### Modules/commands

- [ ] Tra được module bằng `ansible-doc`, biết xem parameters/return/check/diff support.
- [ ] Chọn đúng `package/apt/dnf`, `service/systemd_service`, `file/copy/template`.
- [ ] Dùng được user/group, get_url/unarchive, uri, wait_for, cron và một firewall/mount module phù hợp lab.
- [ ] Giải thích khi nào dùng `command`, khi nào buộc dùng `shell`, và cách giữ idempotency.
- [ ] Dùng được `syntax-check`, `list-hosts`, `check`, `diff`, `limit`, tags và verbosity.

### Safety/idempotency/secrets

- [ ] Từ host sạch, apply thành công; lần hai `changed=0` ngoài thay đổi dự kiến.
- [ ] Sau recap, verify service, process/socket và request thật.
- [ ] Dùng check/diff nhưng nói được giới hạn của simulation.
- [ ] Secret không plaintext trong repo/log/diff; Vault password không commit; file target có mode đúng.
- [ ] Có rollback hoặc snapshot/console plan cho firewall, mount và service change rủi ro.

### Troubleshooting

- [ ] Sửa ít nhất một lỗi ở mỗi layer: inventory, SSH, become, variable/template, handler/service, network/app.
- [ ] Với `unreachable`, chứng minh packet/SSH/auth layer trước khi sửa playbook.
- [ ] Với play xanh nhưng app lỗi, dùng `systemctl`, `journalctl`, `ss`, `curl` để tìm layer.
- [ ] Tìm và sửa một task luôn changed mà không dùng `changed_when: false` để che lỗi.
- [ ] Viết được incident note gồm hypothesis → evidence → root cause → fix → verification → prevention.

### Gate cuối

PASS L3 khi bạn thực hiện được trong một buổi giới hạn thời gian:

1. Reset một Linux VM về snapshot sạch.
2. Chỉ dùng README và documentation, không nhìn tutorial từng bước.
3. Chạy inventory/preflight rồi apply role.
4. Chứng minh user/file/service/socket/HTTP đúng.
5. Chạy lại và đạt `changed=0` ngoài exception đã giải thích.
6. Nhận một lỗi ẩn và định đúng layer trước khi sửa.
7. Bàn giao inventory redacted, playbook/role, hai recaps, verification và incident note.

Nếu lab chỉ chạy được một lần nhưng chưa break/fix, chưa second run hoặc chưa verify ngoài Ansible, trạng thái là **PRACTISING**, chưa phải PASS.

---

## 26. Cheat sheet quyết định nhanh

```text
Cần quản package?                 package / apt / dnf
Cần quản service?                 service / systemd_service
Cần directory/symlink/permission? file
Cần file tĩnh?                    copy
Cần file theo variables?          template
Cần sửa đúng một dòng/block?      lineinfile / blockinfile
Cần user/group?                   user / group
Cần tải artifact?                 get_url + checksum
Cần giải nén?                     unarchive
Cần gọi/check HTTP?               uri
Cần chờ port/file/state?          wait_for
Cần scheduled job?                cron
Cần persistent mount?             ansible.posix.mount
Cần firewall?                     firewalld / ufw phù hợp OS
Có module chuyên dụng?             dùng module đó
Không có, không cần shell feature? command
Thật sự cần pipe/redirect/glob?    shell + quote/guard/failed_when
Config đổi mới restart?            notify + handler
Input bắt buộc?                    assert / mandatory
Muốn xem trước?                    --check --diff --limit one_host
Play xanh?                         vẫn verify service/socket/request
```

---

## 27. Tài liệu chính thức nên bookmark

- [Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks.html)
- [Inventory guide](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html)
- [Using variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html)
- [General precedence rules](https://docs.ansible.com/projects/ansible/latest/reference_appendices/general_precedence.html)
- [Role directory structure](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Handlers](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html)
- [Facts and magic variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_vars_facts.html)
- [Conditionals](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html)
- [Loops](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_loops.html)
- [Tags](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_tags.html)
- [Check and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Ansible Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html)
- [Builtin module index](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/index.html)
- [Ansible configuration settings](https://docs.ansible.com/projects/ansible/latest/reference_appendices/config.html)
- [Ansible CLI tools](https://docs.ansible.com/projects/ansible/latest/command_guide/command_line_tools.html)

Khi documentation online khác codebase công ty, kiểm tra `ansible --version`, version collection và documentation đúng version trước khi kết luận module “sai”.

---

## 28. Câu hỏi tự kiểm tra/phỏng vấn

1. `ansible.builtin.ping` chứng minh gì và không chứng minh gì?
2. Vì sao host `UNREACHABLE` khác task `FAILED`?
3. `ansible_host` khác `inventory_hostname` thế nào?
4. Tại sao role input nên ở `defaults` thay vì `vars`?
5. Khi nào handler chạy và vì sao nhiều notify chỉ restart một lần?
6. `template`, `copy`, `lineinfile` khác nhau ở ownership model nào?
7. Vì sao `shell` thường làm idempotency khó hơn?
8. `changed=0` lần hai có đủ kết luận app healthy không?
9. Check mode có thể bỏ sót điều gì?
10. Vì sao `--diff` nguy hiểm với secret?
11. Vault giải quyết và không giải quyết những vấn đề nào?
12. Service active nhưng remote request timeout: bạn kiểm tra theo thứ tự nào?
13. Terraform output nên đi vào Ansible bằng boundary/data contract nào?
14. Một playbook xanh nhưng ALB target unhealthy có thể sai ở đâu?
15. Evidence nào thuyết phục nhà tuyển dụng rằng bạn đạt L3 thay vì chỉ copy tutorial?

Nếu trả lời được bằng một artifact hoặc incident cụ thể thay vì định nghĩa thuộc lòng, bạn đang đi đúng hướng.
