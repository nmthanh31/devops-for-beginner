# 03. Provider, resource và data source

> [← Quay lại mục lục](./terraform-overview.md)

## Cách học chương này

Chương này có một đích thực hành duy nhất: từ một kubeconfig hợp lệ, chạy được
`terraform plan` cho một Kubernetes Namespace. Làm theo thứ tự:

```text
required_providers → provider configuration → resource → init → plan
```

Nếu `kubectl get nodes` chưa chạy được với cùng kubeconfig/context thì chưa nên
debug Terraform.

## 1. Provider

Provider là plugin cho phép Terraform giao tiếp với API của một nền tảng.

Khai báo provider cần dùng:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

Cấu hình provider:

```hcl
provider "aws" {
  region = "ap-southeast-1"
}
```

| Block | Vai trò |
|---|---|
| `required_providers` | Nguồn và khoảng phiên bản plugin |
| `provider` | Region, project, endpoint, profile và thiết lập runtime |

Sau khi thêm hoặc đổi provider/module, chạy lại `terraform init`.

## 2. Provider theo nền tảng

```hcl
# AWS
provider "aws" {
  region = "ap-southeast-1"
}

# Azure
provider "azurerm" {
  features {}
}

# Google Cloud
provider "google" {
  project = var.project_id
  region  = var.region
}

# Kubernetes
provider "kubernetes" {
  config_path = pathexpand("~/.kube/config")
}
```

Các ví dụ chỉ minh họa cấu trúc. Hãy đọc tài liệu đúng phiên bản provider trước khi dùng trong project thật.

## 3. Xác thực provider

Provider cần credentials để gọi API. Ưu tiên credential chain của nền tảng:

| Nền tảng | Local development | Automation |
|---|---|---|
| AWS | AWS CLI profile | IAM role hoặc OIDC |
| Azure | `az login` | Service Principal, Managed Identity hoặc OIDC |
| GCP | Application Default Credentials | Service account hoặc Workload Identity |
| Kubernetes | Kubeconfig/context | Service account hoặc cơ chế của cluster |

Không hardcode credentials trong provider vì chúng có thể bị đưa vào Git, log, plan hoặc state.

## 4. Resource

Resource là đối tượng Terraform tạo và quản lý:

```hcl
resource "azurerm_resource_group" "main" {
  name     = "rg-demo"
  location = "Southeast Asia"
}
```

Địa chỉ Terraform là `azurerm_resource_group.main`; tên thật trên Azure là `rg-demo`. Hai tên phục vụ mục đích khác nhau.

## 5. Arguments và computed attributes

Argument là giá trị bạn cấu hình:

```hcl
name     = "rg-demo"
location = "Southeast Asia"
```

Computed attribute là giá trị provider/API trả về:

```hcl
azurerm_resource_group.main.id
```

Giá trị hiển thị là `(known after apply)` có nghĩa API chỉ cung cấp nó sau khi tạo resource.

## 6. Data source

Data source đọc thông tin nhưng không tạo tài nguyên:

```hcl
data "aws_caller_identity" "current" {}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
```

```text
resource "aws_vpc" ... → Terraform sở hữu vòng đời VPC
data "aws_vpc" ...     → Terraform chỉ tìm và đọc VPC
```

Data source phù hợp khi tài nguyên do team khác quản lý, cần đọc account/project, tìm image/network có sẵn hoặc đọc dữ liệu từ một dịch vụ khác.

## 7. Provider aliases

Alias cho phép dùng cùng provider với nhiều cấu hình:

```hcl
provider "aws" {
  region = "ap-southeast-1"
}

provider "aws" {
  alias  = "secondary"
  region = "ap-southeast-2"
}

resource "aws_s3_bucket" "primary" {
  bucket_prefix = "primary-"
}

resource "aws_s3_bucket" "secondary" {
  provider      = aws.secondary
  bucket_prefix = "secondary-"
}
```

Provider không có alias là cấu hình mặc định.

## 8. Version constraints và lock file

Provider được phát hành độc lập. Version constraint giới hạn các phiên bản được chấp nhận. Sau `terraform init`, Terraform ghi phiên bản thực tế và checksum vào `.terraform.lock.hcl`.

Nên commit lock file. Chỉ nâng cấp có chủ đích:

```powershell
terraform init -upgrade
```

Sau khi nâng cấp, đọc changelog, review lock file và chạy plan.

## 9. Resource ownership

Terraform giả định mỗi đối tượng thực tế được ánh xạ tới một resource address. Không nên để hai state cùng quản lý một đối tượng.

Nếu tài nguyên đã tồn tại, cần khai báo resource rồi import thay vì tạo một resource address thứ hai trỏ mơ hồ vào cùng đối tượng.

## Thực hành cuối chương: plan một Namespace

Checklist trước Terraform:

```powershell
kubectl config get-contexts --kubeconfig <duong-dan-kubeconfig>
kubectl get nodes --kubeconfig <duong-dan-kubeconfig> --context <context>
```

Trong root module, cần đủ bốn mảnh:

```text
terraform.required_providers
provider "kubernetes"
resource "kubernetes_namespace_v1"
giá trị kubeconfig/context
```

Chạy:

```powershell
terraform init
terraform validate
terraform plan
```

Kết quả mong đợi:

```text
Plan: 1 to add, 0 to change, 0 to destroy
```

Nếu gặp `invalid path`, kiểm tra file bằng `Test-Path` hoặc `ls`. Nếu gặp lỗi
context, so sánh chính xác với cột `NAME` của `kubectl config get-contexts`.

Chỉ chuyển chương khi plan kết thúc không có block `Error`.

## Tài liệu chính thức

- [Providers](https://developer.hashicorp.com/terraform/language/providers)
- [Resources](https://developer.hashicorp.com/terraform/language/resources)
- [Data sources](https://developer.hashicorp.com/terraform/language/data-sources)
- [Dependency lock file](https://developer.hashicorp.com/terraform/language/files/dependency-lock)

