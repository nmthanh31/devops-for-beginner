# 05. Terraform CLI và workflow

> [← Quay lại mục lục](./terraform-overview.md)

## Cách học chương này

Mục tiêu không phải nhớ nhiều lệnh mà là biết **dừng đúng lúc**:

- `init` lỗi: chưa chạy `validate` hay `plan`.
- `validate` lỗi: chưa chạy `plan`.
- `plan` còn `Error`: tuyệt đối chưa chạy `apply`.
- `apply` thành công: luôn chạy lại `plan` để tìm drift.

Thực hành trong `lab2/env/dev`; luôn kiểm tra thư mục hiện tại trước khi chạy.

## 1. Working directory

Terraform chạy trên module trong thư mục hiện tại. Tất cả file `.tf` ở cấp cao nhất được đọc cùng nhau.

```powershell
Set-Location .\my-terraform-project
terraform version
```

Kiểm tra đúng thư mục trước khi chạy để tránh thao tác nhầm state hoặc môi trường.

## 2. `terraform init`

```powershell
terraform init
```

`init`:

- Khởi tạo backend.
- Tải provider plugins.
- Tải child modules.
- Tạo hoặc cập nhật `.terraform.lock.hcl`.
- Chuẩn bị thư mục `.terraform`.

`init` thường không tạo cloud resource. Chạy lại khi thay đổi provider, module hoặc backend.

Các biến thể:

```powershell
terraform init -upgrade       # chọn phiên bản provider/module mới phù hợp constraint
terraform init -reconfigure   # cấu hình lại backend, bỏ qua cấu hình backend đã ghi nhớ
terraform init -migrate-state # di chuyển state khi đổi backend
terraform init -backend=false # khởi tạo mà không truy cập backend
```

Đọc kỹ hướng dẫn trước khi đổi backend hoặc migrate state.

## 3. `terraform fmt`

```powershell
terraform fmt
```

Định dạng file trong thư mục hiện tại. Với CI:

```powershell
terraform fmt -check -recursive
```

`fmt` có thể sửa cách trình bày nhưng không chủ đích thay đổi ý nghĩa cấu hình.

## 4. `terraform validate`

```powershell
terraform validate
```

Kiểm tra:

- Cú pháp HCL.
- Kiểu dữ liệu.
- Tên argument và block theo provider schema.
- Tham chiếu nội bộ.

`validate` không bảo đảm:

- Credentials hợp lệ.
- API có thể truy cập.
- Tài khoản đủ quyền.
- Resource không xung đột.
- Cấu hình đáp ứng yêu cầu production.

`plan` cũng bao gồm validation trong ngữ cảnh chạy thực tế.

## 5. `terraform plan`

```powershell
terraform plan
```

Plan đọc cấu hình, state và thông tin từ provider để tính thay đổi.

| Ký hiệu | Ý nghĩa |
|---|---|
| `+` | Create |
| `~` | Update in-place |
| `-` | Destroy |
| `-/+` | Destroy rồi create replacement |
| `+/-` | Create replacement rồi destroy cũ nếu lifecycle/API cho phép |
| `<=` | Read data source |

Ví dụ:

```text
Plan: 2 to add, 1 to change, 0 to destroy.
```

Lưu plan:

```powershell
terraform plan -out=tfplan
```

Xem plan đã lưu:

```powershell
terraform show tfplan
```

Plan file có thể chứa dữ liệu nhạy cảm; không commit hoặc chia sẻ tùy tiện.

## 6. `terraform apply`

```powershell
terraform apply
```

Nếu không truyền plan file, Terraform tạo plan mới, hiển thị và yêu cầu nhập `yes`.

Áp dụng plan đã duyệt:

```powershell
terraform apply tfplan
```

Tự động bỏ xác nhận:

```powershell
terraform apply -auto-approve
```

Chỉ dùng `-auto-approve` trong automation có kiểm soát. Apply có thể hoàn thành một phần trước khi gặp lỗi; Terraform không tự động rollback toàn bộ.

## 7. Quan sát kết quả

```powershell
terraform show
terraform output
terraform state list
```

Xem một resource trong state:

```powershell
terraform state show aws_s3_bucket.logs
```

Không dùng output CLI làm lý do để coi state là không nhạy cảm.

## 8. Chu trình thay đổi

```text
Sửa .tf
   │
   ▼
terraform fmt
   │
   ▼
terraform validate
   │
   ▼
terraform plan
   │ review
   ▼
terraform apply
   │
   ▼
Kiểm tra hạ tầng và outputs
```

Mỗi lần thay đổi nên chạy lại plan. Không dựa vào plan cũ sau khi code, variables hoặc hạ tầng đã đổi.

## 9. `terraform destroy`

Xem trước:

```powershell
terraform plan -destroy
```

Thực hiện:

```powershell
terraform destroy
```

`destroy` tương đương chế độ apply phá hủy toàn bộ resource đang được state hiện tại quản lý. Luôn xác nhận đúng backend, workspace/account/project trước khi chạy.

## 10. Một workflow nhóm cơ bản

```text
Developer tạo branch
        │
        ▼
fmt + validate + test
        │
        ▼
CI tạo speculative plan
        │
        ▼
Code review + plan review
        │
        ▼
Merge
        │
        ▼
Final plan + approval
        │
        ▼
Apply
```

Không nên cho mọi pull request tự apply vào production mà không có kiểm soát quyền và phê duyệt.

## 11. Các lệnh tra cứu hữu ích

```powershell
terraform -help
terraform plan -help
terraform providers
terraform output -json
terraform show -json tfplan
terraform console
terraform graph
```

`terraform console` giúp thử expressions, còn `terraform graph` xuất dependency graph để phân tích.

## Thực hành cuối chương: workflow có điểm dừng

Thực hiện trong `lab2/env/dev`:

```powershell
terraform fmt -check -recursive ../..
terraform init
terraform validate
terraform plan -out=dev.tfplan
terraform show dev.tfplan
```

Trước apply, tự kiểm tra:

- Đúng Namespace `tf-lab2-dev`.
- Chỉ có application được bật.
- Không có ký hiệu `-` hoặc `-/+` ngoài dự kiến.
- Phần cuối output không có `Error`.

Nếu đạt, chạy:

```powershell
terraform apply dev.tfplan
terraform plan
```

Kết quả cuối phải là:

```text
No changes. Your infrastructure matches the configuration.
```

Nếu không phải `No changes`, đừng apply tiếp. Đọc diff để xác định thay đổi đến
từ code, state hay một hệ thống bên ngoài như Rancher.

## Tài liệu chính thức

- [Terraform CLI](https://developer.hashicorp.com/terraform/cli)
- [`terraform init`](https://developer.hashicorp.com/terraform/cli/commands/init)
- [`terraform plan`](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [`terraform apply`](https://developer.hashicorp.com/terraform/cli/commands/apply)
- [`terraform destroy`](https://developer.hashicorp.com/terraform/cli/commands/destroy)

