# 16. Lab cuối: triển khai ứng dụng hoàn chỉnh

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Đây là bài tích hợp, không phải nơi gom mọi task vào một file. Mỗi phần phải có ownership, input, kiểm tra và điểm dừng rõ. Nếu một checkpoint chưa đạt, không chuyển sang checkpoint sau.

## 1. Kiến trúc mục tiêu

```text
Git branch
   ↓
Merge Request
   ↓
Lint + Syntax Check
   ↓
Check/Diff
   ↓
Review
   ↓
Deploy Dev
   ↓
HTTP + service test
   ↓
Manual Deploy Staging
```

Thành phần:

```text
ansible/
├── .gitlab-ci.yml
├── ansible.cfg
├── README.md
├── inventories/{dev,stag}/
├── playbooks/site.yml
├── roles/{common,nginx,app}/
├── secrets/                  # chỉ chứa ciphertext Vault
└── docs/
```

## 2. Checkpoint thiết kế

### Checkpoint A — Inventory và kết nối

Dev/stag tách biệt, `--list-hosts` đúng, SSH key và sudo hoạt động.

### Checkpoint B — Role contract

`common`, `nginx`, `app` có defaults/README; playbook chính không chứa toàn bộ implementation.

### Checkpoint C — Configuration flow

Template render HTML/config, handler reload chỉ chạy khi file đổi, lần chạy thứ hai không có thay đổi thừa.

### Checkpoint D — Security và quality

Vault ciphertext, `no_log` đúng chỗ, lint/syntax/check pass, không có key/password/kubeconfig trong Git.

### Checkpoint E — Delivery workflow

MR chạy quality gates, dev deploy được, staging là manual/protected và có test sau deploy.

## 3. AWX/Ansible Automation Platform ở mức khái niệm

AWX/Ansible Automation Platform thêm lớp quản trị lên CLI automation:

```text
Project/source control
        ↓
Inventory + credentials + execution environment
        ↓
Job template / workflow / schedule
        ↓
RBAC + audit + output
```

Nó không thay thế kiến thức inventory, playbook, role hay Vault. Hãy hiểu CLI trước, sau đó map CLI concepts vào job template, credential và workflow.

## Thực hành cuối chương: definition of done

Lab đạt khi:

- dev và stag có inventory riêng;
- có role `common`, `nginx`, `app`;
- có Vault ciphertext và không lộ secret;
- có template HTML, handler reload và test HTTP;
- syntax/lint/check/idempotency pass;
- GitLab CI có staging manual;
- README mô tả prerequisites, lệnh, ownership và rollback/repair;
- report review ghi rõ output đã kiểm tra.

## Tài liệu chính thức

- [AWX documentation](https://ansible.readthedocs.io/projects/awx/en/latest/)
- [Red Hat Ansible Automation Platform](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/)
- [Ansible best practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)

