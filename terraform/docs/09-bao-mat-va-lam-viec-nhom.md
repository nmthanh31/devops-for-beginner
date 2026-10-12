# 09. Bảo mật, môi trường và làm việc nhóm

> [← Quay lại mục lục](./terraform-overview.md)

## Cách học chương này

Đừng học bảo mật như một danh sách khẩu hiệu. Với mỗi thay đổi Terraform, trả lời:

1. Credentials nằm ở đâu?
2. State nằm ở đâu và ai đọc được?
3. Plan có hành động xóa hoặc thay thế không?
4. Ai được phép approve và apply?

Cuối chương, bạn phải mô tả được luồng Pull Request → Atlantis plan → review →
`atlantis apply` → merge.

## 1. Mô hình rủi ro

Terraform có thể có quyền tạo, thay đổi và xóa phần lớn hạ tầng. Các khu vực cần bảo vệ:

```text
Source code
Credentials
Plan artifacts
State/backend
CI/CD runner
Provider/module supply chain
Cloud API permissions
Approval process
```

## 2. Không hardcode secrets

Không viết:

```hcl
provider "aws" {
  access_key = "..."
  secret_key = "..."
}
```

Không đặt password thật trong tfvars được commit:

```hcl
database_password = "..."
```

Ưu tiên:

- Short-lived credentials.
- IAM role/Managed Identity/Workload Identity.
- OIDC federation từ CI/CD.
- Secret manager.
- Environment variables được hệ thống CI bảo vệ.

Tránh long-lived access key nếu nền tảng hỗ trợ identity tạm thời.

## 3. Least privilege

Identity chạy Terraform chỉ nên có quyền cần thiết. Tuy nhiên Terraform thường cần cả read và write permissions để refresh, plan và apply.

Có thể tách:

- Identity cho speculative plan.
- Identity cho production apply.
- Quyền quản trị backend.
- Quyền đọc secrets.

Không mặc định dùng owner/admin toàn hệ thống chỉ vì cấu hình dễ chạy hơn.

## 4. Bảo vệ state

State phải được xem như dữ liệu nhạy cảm:

- Mã hóa khi lưu và truyền.
- Giới hạn quyền đọc/ghi.
- Bật versioning/backup.
- Bật locking nếu backend hỗ trợ.
- Audit truy cập.
- Không lưu vào Git.
- Không tải về máy cá nhân nếu không cần.

Không coi `sensitive = true` là mã hóa dữ liệu.

## 5. Bảo vệ plan artifacts

Saved plan có thể chứa:

- Giá trị variables.
- Resource attributes.
- Dữ liệu nhạy cảm từ state/provider.
- Chính xác các thao tác sẽ được apply.

Không commit `tfplan`, không đăng plan chứa secret lên nơi công khai và giới hạn thời gian lưu artifact trong CI.

## 6. Provider và module supply chain

- Chỉ dùng provider/module từ nguồn tin cậy.
- Review publisher và repository.
- Pin version constraint phù hợp.
- Commit `.terraform.lock.hcl`.
- Review thay đổi lock file.
- Đọc changelog khi nâng cấp.
- Không chạy `terraform init -upgrade` vô thức trong mọi pipeline.

## 7. Phân tách môi trường

Development và production nên được tách bằng nhiều lớp:

- Account/subscription/project khác nhau khi có thể.
- State/backend key khác nhau.
- Credentials và quyền khác nhau.
- Pipeline và approval khác nhau.
- Variables và policy khác nhau.

Chỉ thay đổi một variable `environment = "production"` không tạo ra sự cách ly bảo mật thực sự.

## 8. Code review

Reviewer nên kiểm tra cả code và plan.

### Code

- Provider/module source có tin cậy không?
- Version có được kiểm soát không?
- Có hardcode secret không?
- Resource có public ngoài ý muốn không?
- Encryption, backup và logging có phù hợp không?
- `ignore_changes`, `depends_on`, `count` có bị lạm dụng không?

### Plan

- Đúng account, region và môi trường chưa?
- Bao nhiêu resource add/change/destroy?
- Có `-/+` gây replacement không?
- Có database, network, IAM hoặc state resource bị xóa không?
- Có unknown value đáng chú ý không?
- Chi phí có thay đổi đáng kể không?

## 9. Pipeline tham khảo

```text
Pull request
    │
    ├── terraform fmt -check
    ├── terraform init
    ├── terraform validate
    ├── security/static checks
    ├── tests
    └── speculative plan
             │
             ▼
      Code + plan review
             │
             ▼
           Merge
             │
             ▼
        Final plan
             │
             ▼
     Production approval
             │
             ▼
           Apply
```

Không apply production trực tiếp từ laptop cá nhân nếu tổ chức đã có pipeline quản lý.

## 10. Concurrency

- Chỉ một apply được ghi vào một state tại một thời điểm.
- Dùng backend locking.
- Không chạy local apply đồng thời với CI.
- Không force-unlock khi chưa xác nhận tiến trình giữ lock đã dừng.
- Serialize pipeline theo state/environment.

## 11. Blast radius

Giảm phạm vi ảnh hưởng bằng cách:

- Tách state theo lifecycle và ownership.
- Hạn chế số lượng resource quan trọng trong một lần thay đổi.
- Dùng policy/approval cho production.
- Bảo vệ resource quan trọng ở cả Terraform và nền tảng.
- Sao lưu dữ liệu trước migration/replacement.
- Không dùng `-auto-approve` tùy tiện.

## 12. Cost awareness

Terraform có thể tạo tài nguyên tính phí cao:

- NAT Gateway.
- Load Balancer.
- Managed Kubernetes control plane.
- Database và backup.
- Public IP.
- Cross-region traffic.
- Logging và storage.

Plan không phải lúc nào cũng hiển thị chi phí. Cần kết hợp tagging, budget, quota, cost estimation và cleanup policy.

## 13. `.gitignore` cơ bản

```gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
crash.log
crash.*.log
override.tf
override.tf.json
*_override.tf
*_override.tf.json
```

Chính sách đối với tfvars tùy dự án. Nếu file chứa secret, phải ignore hoặc dùng cơ chế khác.

## 14. Quy tắc vận hành production

- Dùng remote backend có backup và locking.
- Dùng identity ngắn hạn và least privilege.
- Mọi thay đổi đi qua version control.
- Plan và apply phải gắn với cùng revision được duyệt.
- Production apply cần approval phù hợp.
- Không sửa thủ công trừ quy trình break-glass.
- Nếu sửa khẩn cấp, phản ánh lại thay đổi vào code/state.
- Theo dõi drift và thất bại apply.
- Kiểm thử restore, không chỉ backup.

## Thực hành cuối chương: review một thay đổi như trong team

Giả sử một Pull Request đổi `frontend.replicas` từ 1 thành 2.

### Review code

- Chỉ `env/stag/terraform.tfvars` thay đổi hay còn file khác?
- Có secrets hoặc kubeconfig bị commit không?
- Module source/provider version có bị đổi ngoài dự kiến không?

### Review plan

Plan đúng phải cho thấy:

```text
0 to add, 1 to change, 0 to destroy
```

Resource thay đổi phải là Deployment frontend của `stag`; Namespace, Service và
resource `dev` không được bị tác động.

### Workflow Atlantis cần mô tả được

```text
Tạo Pull Request
      ↓
Atlantis chạy terraform plan
      ↓
Team review code và plan
      ↓
Approve Pull Request
      ↓
Người có quyền comment: atlantis apply
      ↓
Apply thành công
      ↓
Merge Pull Request
```

Atlantis là service chạy Terraform; nó không thay thế state backend, provider,
Git review hoặc chính sách phân quyền cloud/Kubernetes.

## Tài liệu chính thức

- [Sensitive data in state](https://developer.hashicorp.com/terraform/language/state/sensitive-data)
- [Dependency lock file](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [Running Terraform in automation](https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform)
- [Style guide](https://developer.hashicorp.com/terraform/language/style)

