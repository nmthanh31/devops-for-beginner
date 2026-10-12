# Terraform căn bản: học đến đâu chạy được đến đó

Tài liệu này dùng Kubernetes làm nền tảng thực hành vì bạn đã có cluster và
không cần tài khoản AWS. Các khái niệm Terraform học được vẫn áp dụng cho AWS,
Azure, Google Cloud và những provider khác.

## 1. Bắt đầu từ đâu?

Không đọc hết chín chương rồi mới làm lab. Học theo vòng lặp ngắn:

```text
Đọc một khái niệm
       ↓
Viết một phần cấu hình nhỏ
       ↓
terraform fmt + validate + plan
       ↓
Đọc kết quả và sửa lỗi
       ↓
Mới chuyển sang phần tiếp theo
```

Hai thư mục thực hành chính:

```text
terraform-jun/
├── lab1/   # Một file: Namespace + Deployment + Service
└── lab2/   # Module + for_each + dev/stag
```

- `lab1` giúp hiểu resource, provider và CLI.
- `lab2` giúp hiểu variable, local, module, `for_each` và nhiều môi trường.

## 2. Mô hình cần ghi nhớ

```text
Code .tf
   │
   ▼
Terraform Core ──────── Terraform state
   │
   ▼
Kubernetes provider
   │
   ▼
Kubernetes API
   │
   ▼
Namespace / Deployment / Service
```

| Thành phần | Trả lời câu hỏi |
|---|---|
| File `.tf` | Bạn muốn hạ tầng trông như thế nào? |
| Terraform Core | Cần tạo, sửa hay xóa những gì? |
| Provider | Gọi API Kubernetes bằng cách nào? |
| State | Resource trong code tương ứng đối tượng thật nào? |
| Kubernetes API | Thực sự tạo Namespace, Deployment và Service |

## 3. Quy trình làm việc chuẩn

Luôn chạy theo thứ tự:

```powershell
terraform fmt -recursive
terraform init
terraform validate
terraform plan
terraform apply
terraform plan
```

1. `fmt`: chuẩn hóa định dạng.
2. `init`: tải provider và child module.
3. `validate`: kiểm tra cấu hình và reference.
4. `plan`: xem trước thay đổi.
5. `apply`: thực hiện thay đổi đã review.
6. `plan` lần nữa: xác nhận `No changes`.

Không chạy `apply` nếu phần cuối `plan` còn `Error`.

## 4. Lộ trình học thực hành

| Chương | Kiến thức | Việc phải làm được sau chương |
|---|---|---|
| [01](./01-iac-va-kien-truc-terraform.md) | IaC và kiến trúc | Giải thích đường đi từ `.tf` đến Kubernetes API |
| [02](./02-hcl-can-ban.md) | HCL | Đọc được block, argument, map và reference trong Lab 1 |
| [03](./03-provider-resource-data-source.md) | Provider và resource | Plan được một Namespace trên cluster |
| [04](./04-variables-expressions-va-vong-lap.md) | Variable, local, vòng lặp | Lọc application bằng `for ... if` và tạo bằng `for_each` |
| [05](./05-cli-va-workflow.md) | CLI workflow | Biết dừng ở bước nào khi init/validate/plan lỗi |
| [06](./06-state-backend-va-drift.md) | State và drift | Chứng minh state của `dev` và `stag` tách biệt |
| [07](./07-dependency-lifecycle-va-import.md) | Dependency và lifecycle | Xử lý annotation do Rancher tự thêm mà không có drift lặp lại |
| [08](./08-modules-va-cau-truc-du-an.md) | Module và cấu trúc | Tự tổ chức được Lab 2 theo `shared` và `env` |
| [09](./09-bao-mat-va-lam-viec-nhom.md) | Bảo mật và teamwork | Review plan trước khi apply và mô tả workflow Atlantis |

## 5. Hai mốc thực hành chính

### Mốc A — Lab 1

Bạn hoàn thành Lab 1 khi:

- Provider đọc đúng kubeconfig và context.
- Plan tạo một Namespace, một Deployment và một Service.
- Pod ở trạng thái `Running`.
- Service có endpoint.
- Chạy lại plan nhận `No changes`.

### Mốc B — Lab 2

Bạn hoàn thành Lab 2 khi:

- Namespace và application là các child module.
- `frontend` và `api` được tạo bằng một module block có `for_each`.
- `worker` không được tạo khi `enabled = false`.
- `dev` và `stag` có Namespace và state riêng.
- Thay replicas trong tfvars chỉ update đúng Deployment.
- Chạy lại plan ở từng môi trường nhận `No changes`.

## 6. Cách đọc một lỗi Terraform

Đừng đọc toàn bộ output từ đầu. Tìm block `Error` cuối cùng và đọc theo thứ tự:

```text
Loại lỗi
  └── File và số dòng
       └── Expression gây lỗi
            └── Giá trị Terraform đang nhìn thấy
```

Ví dụ:

```text
Error: Invalid function argument
on providers.tf line 2
config_path = abs(var.kubeconfig_path)
var.kubeconfig_path is "...yaml"
```

Kết luận: `abs()` cần số, còn đường dẫn cần `abspath()`.

Thứ tự xử lý:

1. Đọc block `Error` cuối output.
2. Mở đúng file và dòng được báo.
3. Kiểm tra kiểu dữ liệu và tên reference.
4. Chạy `terraform fmt`.
5. Chạy `terraform validate`.
6. Chạy lại `terraform plan`.

Không sửa nhiều lỗi phỏng đoán cùng lúc.

## 7. Cách biết mình đã hiểu

Sau mỗi phần, bạn phải trả lời được ba câu:

1. Giá trị này đi từ file nào sang file nào?
2. Terraform address của resource là gì?
3. Tôi dùng lệnh nào để chứng minh cấu hình hoạt động?

Ví dụ với Namespace trong Lab 2:

```text
env/dev/terraform.tfvars
        ↓
env/dev/main.tf
        ↓
shared/locals.tf
        ↓
module.namespace
        ↓
kubernetes_namespace_v1.this
```

Nếu chưa mô tả được đường đi này, chưa nên thêm resource mới.

## 8. Quy tắc an toàn

- Luôn kiểm tra đúng thư mục `env/dev` hay `env/stag` trước khi chạy.
- Kiểm tra kubeconfig và context trước `plan`/`apply`.
- Đọc các ký hiệu `+`, `~`, `-` và `-/+` trong plan.
- Không apply khi plan còn lỗi hoặc có destroy ngoài dự kiến.
- Không commit kubeconfig, token, state hoặc plan artifact.
- Nên commit `.terraform.lock.hcl`.
- Không xóa state để “sửa lỗi”; state mất có thể khiến Terraform muốn tạo trùng.
- Sau apply luôn chạy plan lại để kiểm tra idempotency.

## 9. Khi bị kẹt

Ghi lại bốn thông tin:

```text
1. Thư mục đang chạy Terraform
2. Lệnh vừa chạy
3. Block Error đầy đủ
4. Nội dung file và dòng được báo lỗi
```

## Tài liệu chính thức

- [Terraform overview](https://developer.hashicorp.com/terraform/intro)
- [Terraform language](https://developer.hashicorp.com/terraform/language)
- [Terraform CLI](https://developer.hashicorp.com/terraform/cli)
- [Kubernetes provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
