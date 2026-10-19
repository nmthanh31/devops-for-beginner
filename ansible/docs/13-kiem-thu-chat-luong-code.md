# 13. Kiểm thử và chất lượng code

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Quality gate không phải một lệnh duy nhất. Học theo tầng: YAML → syntax → lint → check/diff → runtime test → idempotency. Mỗi tầng bắt một loại lỗi khác nhau.

## 1. Các lớp kiểm tra

| Lớp | Câu hỏi |
|---|---|
| YAML lint | File có cấu trúc YAML hợp lệ và nhất quán không? |
| Syntax check | Playbook/import/module reference có parse được không? |
| `--check` | Nếu chạy, Ansible dự đoán đổi gì? |
| `--diff` | File sẽ đổi nội dung nào? |
| `ansible-lint` | Có anti-pattern/security/style issue không? |
| Runtime test | Service/file/HTTP thực sự đúng không? |
| Idempotency | Lần chạy thứ hai còn thay đổi không? |

Không thay thế runtime test bằng lint. Không coi `--check` là mô phỏng hoàn hảo cho mọi module/command.

## 2. Lint và naming

FQCN như `ansible.builtin.package` làm rõ module đến từ collection nào. Tên task rõ giúp đọc log. Rule lint nên được sửa ở code; `skip_list` chỉ dùng khi có lý do và review.

## 3. Molecule ở mức cơ bản

Molecule tạo scenario để converge role rồi verify bằng container/VM. Một scenario thường có:

```text
roles/nginx/molecule/default/
├── molecule.yml
├── converge.yml
└── verify.yml
```

Molecule không làm biến mất nhu cầu test môi trường thật; nó là lớp kiểm tra role tái lập được.

## Lệnh cần chạy

**Git Bash/WSL — control node:**

```bash
yamllint .
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --syntax-check
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --check
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --check --diff
ansible-lint
```

## Thực hành cuối chương: quality gate local

Chạy bốn lệnh trên trước khi mở Merge Request. Lưu lại warning và giải thích mọi exception. Sau đó tạo verify test cho role: package tồn tại, service active, config hợp lệ, HTTP trả về expected content.

## Tài liệu chính thức

- [ansible-lint](https://ansible.readthedocs.io/projects/lint/)
- [Check mode](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Molecule documentation](https://ansible.readthedocs.io/projects/molecule/)

