# Ansible căn bản: học đến đâu chạy được đến đó

Tài liệu này dùng các VM Linux nội bộ, container hoặc Kubernetes local làm nền tảng thực hành. Không cần AWS/GCP/Azure. Cách học được tổ chức tương tự `terraform/docs`: đọc mental model, xem ví dụ nhỏ, chạy checkpoint, đọc output và chỉ chuyển chương khi chứng minh được trạng thái.

## 1. Bắt đầu từ đâu?

Không đọc hết rồi mới chạy lab. Học theo vòng lặp ngắn:

```text
Đọc một khái niệm
       ↓
Đọc một ví dụ nhỏ
       ↓
Chạy lệnh quan sát/check
       ↓
Đọc recap và giải thích kết quả
       ↓
Mới chuyển sang phần tiếp theo
```

Mục tiêu không phải thuộc mọi module. Mục tiêu là nhìn được đường đi:

```text
Playbook → inventory/pattern → SSH → module → managed node → recap
```

## 2. Mô hình cần ghi nhớ

```text
Developer → Git/MR → CI/control node
                         ↓ SSH/API
              dev/stag managed nodes
                         ↓
                 OS + Nginx + App
```

| Thành phần | Vai trò |
|---|---|
| Control node | Nơi cài Ansible và chạy automation |
| Managed node | Máy nhận module và thay đổi |
| Inventory | Target, group, host variables và connection variables |
| Playbook | Trạng thái mong muốn theo YAML |
| Role | Đóng gói capability có interface |
| Handler | Phản ứng khi configuration thay đổi |
| Vault | Mã hóa secret trong repository |

## 3. Quy trình làm việc chuẩn

Từ control node, workflow cơ bản là:

```bash
ansible-inventory -i inventories/dev/hosts.yml --graph
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --syntax-check
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --check --diff
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --check
```

1. `ansible-inventory`: xác nhận target.
2. `--syntax-check`: bắt lỗi parse/import sớm.
3. `--check --diff`: xem thay đổi dự kiến, cẩn thận secret trong diff.
4. Chạy thật sau khi đã review.
5. Chạy lại để kiểm tra idempotency.

Không chạy deploy staging nếu inventory/target chưa được xác nhận hoặc check còn lỗi.

## 4. Lộ trình học thực hành

| Chương | Kiến thức | Việc phải làm được sau chương |
|---|---|---|
| [00](./00-tong-quan-ansible.md) | Kiến trúc Ansible | Mô tả flow control → managed node và ranh giới Terraform |
| [01](./01-chuan-bi-moi-truong-lab.md) | Control/managed node, SSH | `whoami` bằng key tới dev và stag |
| [02](./02-cai-dat-ansible.md) | Cài đặt, config, project | Tạo project có config và dependency rõ |
| [03](./03-inventory.md) | Inventory, pattern, variables | Chứng minh đúng host trước khi chạy |
| [04](./04-ad-hoc-commands.md) | Module và ad-hoc | Chọn module thay vì shell khi có thể |
| [05](./05-playbook-co-ban.md) | Playbook | Viết playbook Nginx nhỏ |
| [06](./06-idempotency.md) | State và recap | Lần chạy thứ hai không đổi thừa |
| [07](./07-variables-facts-conditionals-loops.md) | Dữ liệu và flow | Dùng chung playbook cho dev/stag |
| [08](./08-handlers-templates-files.md) | File/template/handler | Render config và reload có điều kiện |
| [09](./09-roles.md) | Role interface | Tách `common`, `nginx`, `app` |
| [10](./10-quan-ly-nhieu-moi-truong.md) | Environment boundary | Không deploy nhầm inventory |
| [11](./11-ansible-vault.md) | Secret | Không lộ plaintext trong Git/log |
| [12](./12-error-handling-troubleshooting.md) | Chẩn đoán | Phân loại lỗi trước khi sửa |
| [13](./13-kiem-thu-chat-luong-code.md) | Quality gates | Lint/syntax/check/runtime test |
| [14](./14-gitlab-ci-cho-ansible.md) | GitLab CI | Dev tự động, staging manual |
| [15](./15-ket-hop-terraform-ansible.md) | Ownership Terraform/Ansible | Truyền output thành inventory |
| [16](./16-lab-cuoi.md) | Tích hợp | Hoàn thành workflow từ MR tới staging |

## Lab ngắn khởi động

- [Lab 00 — SSH key, inventory và Ansible ping](../ansible-jun/lab1/README.md): làm trước các chương chính để hiểu từng lớp.
- [Lab 02 — Ad-hoc commands và idempotency](../ansible-jun/lab2/README.md): làm sau Lab 00, trước khi viết playbook.

## 5. Hai mốc thực hành chính

### Mốc A — Web lab

Hoàn thành khi:

- control node SSH được vào dev/stag;
- inventory group `dev`, `stag`, `web` đúng;
- playbook cài Nginx và tạo HTML;
- chạy lại không có thay đổi thừa;
- template/handler hoạt động.

### Mốc B — Project có workflow

Hoàn thành khi:

- role `common`, `nginx`, `app` được tái sử dụng;
- inventory dev/stag tách biệt;
- secret dùng Vault;
- lint/syntax/check chạy trong GitLab CI;
- staging là manual/protected;
- README mô tả ownership và lệnh kiểm tra.

## 6. Cách đọc một lỗi Ansible

Đừng đọc toàn bộ log từ đầu. Tìm task fail/unreachable và đọc theo flow:

```text
Target/pattern
  └── Inventory/connection
       └── SSH/become/Python
            └── Module arguments/data
                 └── Desired state
```

Khi gửi lỗi, luôn kèm:

```text
1. Thư mục/control node đang chạy
2. Lệnh đầy đủ
3. Inventory và --limit
4. Error block đã che secret
5. Lệnh kiểm tra đã thử
```

Không sửa nhiều file theo phỏng đoán cùng lúc.

## 7. Cách biết mình đã hiểu

Sau mỗi chương, trả lời ba câu:

1. Dữ liệu này đến từ file/biến nào?
2. Task đang tác động host nào và chạy ở đâu?
3. Lệnh nào chứng minh trạng thái đã đúng và chạy lại không đổi?

Ví dụ:

```text
inventories/dev/group_vars/all.yml
        ↓
playbooks/site.yml
        ↓
role.nginx template
        ↓
managed node /etc/nginx/conf.d/app.conf
        ↓
handler reload + HTTP check
```

## 8. Quy tắc an toàn

- Luôn kiểm tra đúng thư mục và inventory trước deploy.
- Không commit private key, Vault password, password plaintext hoặc kubeconfig.
- Không dùng `shell` nếu module chuyên dụng đáp ứng được.
- Không dùng `--diff` với file có secret nếu chưa kiểm soát output.
- Staging phải có review/manual approval.
- Không sửa managed node thủ công để che lỗi automation.
- Không để Terraform và Ansible cùng quản lý một resource/file.

## Tài liệu hiện có trong repository

- [Ansible handbook](../ansible-jun/jun/ANSIBLE-HANDBOOK-JUNIOR-DEVOPS.md): tra cứu sâu hơn.
- [Lab inventory hiện có](../ansible-jun/jun/inventories/lab/inventory.ini): chỉ dùng sau khi hiểu inventory và xác nhận target.

## Tài liệu chính thức

- [Ansible documentation](https://docs.ansible.com/ansible/latest/)
- [Getting started](https://docs.ansible.com/ansible/latest/get_started/index.html)
- [Ansible best practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)

