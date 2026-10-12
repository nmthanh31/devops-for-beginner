# 08. Modules và cấu trúc dự án

> [← Quay lại mục lục](./terraform-overview.md)

## Cách học chương này

Không bắt đầu bằng một cây thư mục lớn. Tách Lab 2 theo từng mốc chạy được:

1. Module Namespace → plan được một Namespace.
2. Module Application → tạo được một Deployment và Service.
3. `for_each` → tạo `frontend` và `api`.
4. `env/dev` chạy ổn → mới tạo `env/stag`.

Sau mỗi mốc, `validate` phải thành công và plan phải đúng trước khi thêm tầng mới.

## 1. Module là gì?

Mọi thư mục chứa cấu hình Terraform đều là một module.

- Thư mục bạn chạy `terraform plan` là **root module**.
- Module được root module gọi là **child module**.

Một module thường gồm:

- Input variables.
- Resources và data sources.
- Local values.
- Outputs.
- Yêu cầu provider.

## 2. Vì sao dùng module?

Module phù hợp khi một nhóm tài nguyên:

- Được tạo lặp lại.
- Có một trách nhiệm rõ ràng.
- Cần giao diện input/output ổn định.
- Cần chuẩn hóa giữa các team hoặc môi trường.

Ví dụ module network:

```text
network module
├── VPC/VNet
├── subnets
├── route tables
├── NAT
└── network security rules
```

Không nên biến mọi resource đơn lẻ thành module. Abstraction quá sớm làm code khó theo dõi.

## 3. Module đơn giản

Cấu trúc:

```text
modules/
└── network/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── README.md
```

`variables.tf`:

```hcl
variable "name" {
  type        = string
  description = "Tên network"
}

variable "cidr_block" {
  type        = string
  description = "CIDR của network"
}
```

`main.tf`:

```hcl
resource "aws_vpc" "this" {
  cidr_block = var.cidr_block

  tags = {
    Name = var.name
  }
}
```

`outputs.tf`:

```hcl
output "id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}
```

## 4. Gọi child module

```hcl
module "network" {
  source = "./modules/network"

  name       = "development"
  cidr_block = "10.0.0.0/16"
}
```

Dùng output:

```hcl
resource "aws_subnet" "application" {
  vpc_id     = module.network.id
  cidr_block = "10.0.1.0/24"
}
```

## 5. Module sources

Module có thể đến từ:

- Đường dẫn local.
- Terraform Registry.
- Git repository.
- Object storage hoặc nguồn được Terraform hỗ trợ.

Registry module:

```hcl
module "network" {
  source  = "organization/network/aws"
  version = "x.y.z"

  # inputs
}
```

Nên pin version module từ registry. Với Git source, nên pin tag hoặc commit thay vì phụ thuộc vào branch có thể thay đổi.

## 6. Provider trong module

Provider configuration nên nằm ở root module. Child module khai báo provider requirement nhưng thường nhận cấu hình provider từ parent.

Root module có alias:

```hcl
provider "aws" {
  alias  = "secondary"
  region = "ap-southeast-2"
}

module "replica" {
  source = "./modules/storage"

  providers = {
    aws = aws.secondary
  }
}
```

Tránh hardcode account, region hoặc credentials trong reusable module.

## 7. Tạo nhiều module instances

```hcl
module "environment" {
  for_each = {
    development = "10.10.0.0/16"
    staging     = "10.20.0.0/16"
  }

  source = "./modules/network"

  name       = each.key
  cidr_block = each.value
}
```

Tham chiếu:

```hcl
module.environment["development"].id
```

## 8. Cấu trúc project nhỏ

```text
project/
├── terraform.tf
├── providers.tf
├── variables.tf
├── locals.tf
├── main.tf
├── outputs.tf
├── terraform.tfvars
└── .gitignore
```

| File | Vai trò |
|---|---|
| `terraform.tf` | Required version, providers, backend |
| `providers.tf` | Provider configurations |
| `variables.tf` | Input interface |
| `locals.tf` | Giá trị tính toán và dùng lại |
| `main.tf` | Resources, data sources và module calls |
| `outputs.tf` | Output interface |
| `terraform.tfvars` | Giá trị cho một lần chạy/môi trường |

Tên file chỉ là quy ước; Terraform đọc chúng cùng nhau.

## 9. Tổ chức nhiều môi trường

Có nhiều chiến lược. Một cách dễ hiểu là tách root module/state theo môi trường:

```text
infrastructure/
├── modules/
│   ├── network/
│   └── application/
└── environments/
    ├── development/
    │   ├── main.tf
    │   └── backend.tf
    ├── staging/
    │   ├── main.tf
    │   └── backend.tf
    └── production/
        ├── main.tf
        └── backend.tf
```

Ưu điểm:

- State tách biệt.
- Quyền truy cập tách biệt.
- Dễ hiểu blast radius.
- Production không phụ thuộc vào việc chọn đúng CLI workspace thủ công.

Nhược điểm là có thể lặp root configuration; reusable modules giúp giảm lặp.

## 10. Module interface tốt

Một module tốt nên:

- Có trách nhiệm rõ ràng.
- Input vừa đủ, có type và description.
- Không để người dùng phải biết chi tiết nội bộ không cần thiết.
- Output những giá trị cần kết nối với module khác.
- Có validation cho điều kiện quan trọng.
- Không hardcode môi trường hoặc credentials.
- Có README và ví dụ.
- Pin hoặc khai báo rõ compatibility của provider.

## 11. Khi nào nên tách state, khi nào chỉ tách module?

Tách module để tái sử dụng code không đồng nghĩa tách state. Child module vẫn nằm trong state của root module gọi nó.

Tách state khi cần khác nhau về:

- Lifecycle.
- Quyền sở hữu.
- Quyền truy cập.
- Tần suất thay đổi.
- Blast radius.
- Account/subscription/project.

## Thực hành cuối chương: xây Lab 2 theo checkpoint

### Checkpoint A — Namespace module

Interface:

```text
inputs:  name, labels
output:  name
creates: kubernetes_namespace_v1
```

Gọi từ shared module và plan được đúng một Namespace trước khi làm application.

### Checkpoint B — Application module

Interface:

```text
inputs:  name, namespace, image, replicas,
         container_port, service_port, labels
outputs: deployment_name, service_name
creates: kubernetes_deployment_v1, kubernetes_service_v1
```

Selector Deployment, Pod labels và selector Service phải thống nhất key `app`.

### Checkpoint C — Nhiều application

Shared module lọc `applications`, sau đó gọi Application module bằng `for_each`.
Plan dev phải tạo hai application khi worker bị tắt.

### Checkpoint D — Environment roots

```text
env/dev  → gọi ../../shared với tfvars của dev
env/stag → gọi ../../shared với tfvars của stag
```

Provider configuration nằm trong environment root. Child module chỉ khai báo
provider requirement, không chứa kubeconfig/context.

### Definition of done

- `fmt -check` và `validate` thành công.
- Plan không còn lỗi.
- State dev/stag tách biệt.
- Pod Running và Service có endpoint.
- Chạy plan sau apply nhận `No changes`.

## Tài liệu chính thức

- [Modules overview](https://developer.hashicorp.com/terraform/language/modules)
- [Use modules](https://developer.hashicorp.com/terraform/language/modules/configuration)
- [Develop modules](https://developer.hashicorp.com/terraform/language/modules/develop)
- [Standard module structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure)

