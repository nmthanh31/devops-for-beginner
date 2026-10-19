# 15. Kết hợp Terraform và Ansible

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Hãy vẽ ownership trước khi nối hai công cụ. Câu hỏi không phải “dùng được cả hai không?”, mà là “resource nào có một owner rõ ràng và output nào là contract giữa hai bên?”.

## 1. Hai lớp lifecycle

```text
Terraform
└── network, VM, DNS, Kubernetes resources, database

Ansible
└── package, OS config, Nginx, app files, systemd service
```

Terraform thường dùng provider/API và state. Ansible thường dùng SSH/API và module. Terraform không nên sở hữu file `/etc/nginx/nginx.conf` nếu Ansible đã sở hữu file đó.

## 2. Contract bằng output

```hcl
output "web_ip" {
  value = module.web.ip_address
}
```

Output Terraform có thể được chuyển thành inventory generated:

```text
terraform apply
     ↓ output IP/hostname
generate inventory
     ↓
ansible --check
     ↓
ansible deploy
```

Private key không nên đi qua Terraform state/output chỉ để tiện truyền sang Ansible.

## 3. Readiness và failure boundary

VM tạo xong chưa chắc SSH đã sẵn sàng. Cần có readiness check, retry hợp lý và inventory regeneration. Nếu Terraform apply thành công nhưng Ansible fail, hai hệ thống không rollback như một transaction; runbook phải biết cách retry/repair.

## Lệnh tham khảo

**Git Bash/WSL — Terraform root:**

```bash
terraform output -json > ../ansible/inventories/generated/terraform-output.json
```

**Git Bash/WSL — Ansible control node:**

```bash
ansible-inventory -i inventories/generated/hosts.yml --graph
ansible-playbook -i inventories/generated/hosts.yml playbooks/site.yml --check
```

## Thực hành cuối chương: ownership review

Viết bảng resource/owner cho lab của bạn. Dùng output giả lập hoặc output local để sinh inventory, rồi chứng minh Ansible chỉ quản lý configuration/application. Không cần dùng cloud.

## Tài liệu chính thức

- [Terraform outputs](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Ansible inventory guide](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
- [Terraform provisioners](https://developer.hashicorp.com/terraform/language/resources/provisioners/syntax) — đọc để hiểu vì sao không nên dùng như integration mặc định

