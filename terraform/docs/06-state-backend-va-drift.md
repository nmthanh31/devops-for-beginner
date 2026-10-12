# 06. State, backend, locking và drift

> [← Quay lại mục lục](./terraform-overview.md)

## Cách học chương này

Hãy coi state là sổ ánh xạ, không phải bản sao Kubernetes:

```text
Terraform address ↔ Kubernetes object ID
```

Mục tiêu thực hành là chứng minh `env/dev` và `env/stag` có hai state khác nhau.
Không xóa, chép đè hoặc khôi phục state khi chưa so sánh với tài nguyên thật.

## 1. State là gì?

Terraform state là cơ sở dữ liệu ánh xạ resource address trong code với đối tượng thật.

```text
aws_instance.web
       │
       ▼
EC2 instance i-0123456789abcdef0
```

State giúp Terraform biết:

- Resource nào đã được tạo.
- Remote ID là gì.
- Thuộc tính gần nhất đã biết.
- Quan hệ và metadata cần thiết.
- Resource nào cần update, replace hoặc destroy.

## 2. Local state

Backend mặc định lưu state trong:

```text
terraform.tfstate
```

Terraform có thể tạo backup:

```text
terraform.tfstate.backup
```

Local state phù hợp cho bài học cá nhân, nhưng không phù hợp cho cộng tác vì:

- Khó chia sẻ an toàn.
- Không có quy trình khóa dùng chung đáng tin cậy giữa nhiều máy.
- Dễ mất hoặc ghi đè.
- Có nguy cơ bị commit vào Git.

## 3. State có thể chứa secrets

State có thể chứa:

- Password và connection string.
- Token hoặc key do API trả về.
- IP nội bộ.
- Resource IDs.
- Metadata hạ tầng.
- Output values.

```hcl
output "password" {
  value     = random_password.database.result
  sensitive = true
}
```

`sensitive = true` chủ yếu che hiển thị; giá trị vẫn có thể nằm trong state. Cần mã hóa, phân quyền và audit backend.

## 4. Backend

Backend xác định nơi lưu state và cách Terraform thao tác với state.

Ví dụ thường gặp:

- Local backend.
- HCP Terraform.
- Amazon S3 backend.
- AzureRM backend.
- Google Cloud Storage backend.

Backend block ví dụ khái niệm:

```hcl
terraform {
  backend "s3" {
    bucket = "company-terraform-state"
    key    = "network/production.tfstate"
    region = "ap-southeast-1"
  }
}
```

Không đặt secrets trực tiếp trong backend config nếu có thể dùng environment, CLI configuration hoặc identity của runtime.

## 5. State locking

Khi backend hỗ trợ locking, Terraform khóa state trong thao tác có thể ghi:

```text
Process A ──► lock state ──► apply ──► write state ──► unlock
Process B ──► chờ hoặc thất bại khi state đang bị khóa
```

Locking ngăn hai tiến trình cùng cập nhật một state và làm mất dữ liệu. Không vô hiệu hóa lock chỉ để vượt lỗi. `force-unlock` chỉ dùng khi chắc chắn lock bị kẹt và không có tiến trình hợp lệ đang chạy.

## 6. State refresh

Trước khi lập kế hoạch, Terraform dùng provider đọc hạ tầng để cập nhật hiểu biết về trạng thái thực tế.

Ba phía được so sánh:

```text
Configuration ←→ State ←→ Remote infrastructure
```

State không thay thế hạ tầng thật, và code vẫn là mô tả mong muốn.

## 7. Drift

Drift là chênh lệch phát sinh khi tài nguyên thật bị thay đổi ngoài workflow Terraform.

Ví dụ:

```text
Code:            instance_type = "small"
Cloud hiện tại:  instance_type = "large"
```

Plan có thể đề xuất đổi lại về `small`. Tuy nhiên, hành vi cụ thể phụ thuộc schema provider, thuộc tính computed và lifecycle configuration.

Nguyên nhân drift:

- Sửa thủ công trên cloud console.
- Một hệ thống automation khác sửa cùng tài nguyên.
- Cloud service tự điều chỉnh thuộc tính.
- Hai Terraform state quản lý cùng đối tượng.
- Provider chuẩn hóa giá trị khác với cấu hình.

## 8. Refresh-only

Khi cần xem hoặc cập nhật state để phản ánh thay đổi ngoài Terraform mà không cố đưa hạ tầng về cấu hình ngay lập tức:

```powershell
terraform plan -refresh-only
terraform apply -refresh-only
```

Phải review kỹ vì refresh-only chấp nhận trạng thái remote vào state/output, nhưng không tự sửa code cho phù hợp.

## 9. Các lệnh state

Các lệnh đọc thường dùng:

```powershell
terraform state list
terraform state show <address>
terraform show
terraform output
```

Các lệnh sửa state như `state mv`, `state rm`, `import` và `force-unlock` có rủi ro cao hơn. Luôn:

1. Xác nhận đúng backend/workspace.
2. Sao lưu state nếu workflow cho phép.
3. Đảm bảo không có apply khác đang chạy.
4. Chạy plan ngay sau thao tác.

## 10. Mất state thì sao?

Mất state không nhất thiết xóa hạ tầng thật, nhưng Terraform mất ánh xạ và có thể đề xuất tạo resource trùng hoặc gặp lỗi conflict.

Cách phục hồi phụ thuộc tình huống:

- Khôi phục phiên bản state từ backend.
- Import tài nguyên vào state mới.
- Tái tạo outputs và dependencies.

Do đó remote backend cần versioning, backup, encryption và kiểm soát truy cập phù hợp.

## 11. Phân tách state

Không nên đặt toàn bộ tổ chức vào một state khổng lồ. Có thể tách theo:

- Môi trường: development, staging, production.
- Account/subscription/project.
- Tầng: network, platform, database, application.
- Nhóm sở hữu và lifecycle.
- Blast radius và quyền truy cập.

Không nên tách chỉ vì muốn có nhiều file `.tf`; nhiều file trong cùng module vẫn dùng chung state.

## 12. Git ignore

```gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
crash.log
```

Nên commit:

```text
*.tf
.terraform.lock.hcl
```

Chỉ commit tfvars khi chắc chắn không chứa secrets và đó là chính sách phù hợp của dự án.

## Thực hành cuối chương: chứng minh state tách biệt

Tại `lab2/env/dev`:

```powershell
terraform state list
terraform output
```

Ghi lại Namespace và các resource address. Làm tương tự tại `env/stag`.

Kết quả đúng:

| Root module | Chỉ được quản lý |
|---|---|
| `env/dev` | Resource trong `tf-lab2-dev` |
| `env/stag` | Resource trong `tf-lab2-stag` |

Tiếp theo chạy `terraform plan` ở từng thư mục. Một plan của `stag` không được
đề xuất thay đổi resource `dev`.

### Bài thử drift an toàn

Chỉ quan sát annotation do Rancher tự thêm vào Namespace; không sửa/xóa resource
thủ công. Nếu plan liên tục muốn xóa annotation do Rancher quản lý, đó là drift
do controller bên ngoài.

### Khi plan muốn tạo lại mọi thứ

Dừng lại và kiểm tra:

```powershell
terraform state list
Get-ChildItem -Force *.tfstate*
kubectl get namespace
```

- State rỗng, tài nguyên còn: cần điều tra/import, không apply tạo trùng.
- State rỗng, tài nguyên không còn: plan create là hợp lý.
- Backup có resource nhưng cluster không còn: không khôi phục backup một cách mù
  quáng vì sẽ tạo state sai với thực tế.

## Tài liệu chính thức

- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [State purpose](https://developer.hashicorp.com/terraform/language/state/purpose)
- [Backends](https://developer.hashicorp.com/terraform/language/backend)
- [State locking](https://developer.hashicorp.com/terraform/language/state/locking)

