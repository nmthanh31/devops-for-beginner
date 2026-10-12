# 04. Variables, expressions, điều kiện và vòng lặp

> [← Quay lại mục lục](./terraform-overview.md)

Terraform là ngôn ngữ khai báo. Nó không có `for`, `while`, `if/else`, `break` và `continue` dạng câu lệnh tuần tự như Python hoặc Java. Thay vào đó, HCL dùng expressions để tạo giá trị và meta-arguments để tạo nhiều resource.

## Cách học chương này

Đây là chương dễ gây rối nhất, nên học theo ba tầng và không nhảy cóc:

1. `variable`: dữ liệu đi vào module.
2. `local`: dữ liệu được tính hoặc lọc bên trong module.
3. `for_each`: tạo nhiều instance từ map đã chuẩn bị.

Ví dụ xuyên suốt là map `applications` trong Lab 2. Chỉ khi nhìn được giá trị
`local.enabled_applications` mới chuyển sang viết module có `for_each`.

## 1. Input variables

```hcl
variable "environment" {
  description = "Tên môi trường triển khai"
  type        = string
  default     = "development"
}
```

Sử dụng:

```hcl
tags = {
  Environment = var.environment
}
```

Một variable nên có:

- Tên rõ nghĩa.
- `description`.
- `type` cụ thể.
- `default` nếu thực sự có mặc định an toàn.
- `sensitive = true` nếu đầu vào nhạy cảm.
- Validation khi có giới hạn nghiệp vụ.

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "environment phải là development, staging hoặc production."
  }
}
```

## 2. Cung cấp giá trị variable

### Default

```hcl
default = "development"
```

### `terraform.tfvars`

```hcl
environment = "staging"
```

### File được chỉ định

```powershell
terraform plan -var-file="production.tfvars"
```

### Command line

```powershell
terraform plan -var="environment=production"
```

### Environment variable

```powershell
$env:TF_VAR_environment = "production"
```

Không nên đặt secrets trong file tfvars được commit.

## 3. Complex variable types

```hcl
variable "servers" {
  type = map(object({
    instance_type = string
    enabled       = bool
    tags          = map(string)
  }))

  default = {
    web = {
      instance_type = "small"
      enabled       = true
      tags          = { Role = "frontend" }
    }

    api = {
      instance_type = "medium"
      enabled       = true
      tags          = { Role = "backend" }
    }
  }
}
```

Type constraint giúp Terraform báo lỗi sớm khi dữ liệu đầu vào sai cấu trúc.

## 4. Local values

Locals đặt tên cho biểu thức được dùng lại:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

Sử dụng:

```hcl
name = "${local.name_prefix}-web"
tags = local.common_tags
```

Variable là đầu vào của module; local là giá trị nội bộ được tính từ input hoặc dữ liệu khác.

## 5. Output values

```hcl
output "resource_group_id" {
  description = "ID của Azure Resource Group"
  value       = azurerm_resource_group.main.id
}
```

Output nhạy cảm:

```hcl
output "connection_string" {
  value     = some_database.main.connection_string
  sensitive = true
}
```

`sensitive` che giá trị trong giao diện thông thường nhưng không loại nó khỏi state.

## 6. Conditional expression

Cú pháp tương đương `if/else`:

```hcl
condition ? value_if_true : value_if_false
```

Ví dụ:

```hcl
locals {
  instance_type = var.environment == "production" ? "large" : "small"
}
```

Nhiều nhánh có thể lồng nhau nhưng nhanh chóng khó đọc:

```hcl
locals {
  size = (
    var.environment == "production" ? "large" :
    var.environment == "staging"    ? "medium" :
    "small"
  )
}
```

Map thường rõ hơn:

```hcl
locals {
  sizes = {
    development = "small"
    staging     = "medium"
    production  = "large"
  }

  size = lookup(local.sizes, var.environment, "small")
}
```

## 7. Tạo resource có điều kiện

```hcl
resource "aws_s3_bucket" "backup" {
  count = var.enable_backup ? 1 : 0

  bucket_prefix = "backup-"
}
```

Khi dùng `count`, địa chỉ có index:

```text
aws_s3_bucket.backup[0]
```

Tham chiếu an toàn có thể dùng điều kiện hoặc `try`:

```hcl
output "backup_bucket" {
  value = try(aws_s3_bucket.backup[0].bucket, null)
}
```

## 8. `count`

`count` tạo nhiều instance gần giống nhau:

```hcl
resource "aws_instance" "web" {
  count = 3

  ami           = var.ami_id
  instance_type = "t3.micro"

  tags = {
    Name = "web-${count.index + 1}"
  }
}
```

Địa chỉ:

```text
aws_instance.web[0]
aws_instance.web[1]
aws_instance.web[2]
```

Nếu xóa phần tử giữa một danh sách dựa trên index, các index sau có thể dịch chuyển. Vì vậy resource có danh tính riêng thường phù hợp với `for_each` hơn.

## 9. `for_each`

```hcl
variable "resource_groups" {
  type = map(string)

  default = {
    application = "Southeast Asia"
    monitoring  = "East Asia"
  }
}

resource "azurerm_resource_group" "this" {
  for_each = var.resource_groups

  name     = "rg-${each.key}"
  location = each.value
}
```

Địa chỉ ổn định theo key:

```text
azurerm_resource_group.this["application"]
azurerm_resource_group.this["monitoring"]
```

`for_each` nhận map hoặc set of strings. Chuyển list sang set khi phù hợp:

```hcl
for_each = toset(var.names)
```

Không thể dùng `count` và `for_each` đồng thời trong cùng block.

## 10. `for` expression

Biến đổi list:

```hcl
locals {
  uppercase_names = [
    for name in var.names : upper(name)
  ]
}
```

Dùng index:

```hcl
locals {
  numbered_names = [
    for index, name in var.names : "${index + 1}-${name}"
  ]
}
```

Tạo map:

```hcl
locals {
  server_names = {
    for key, server in var.servers :
    key => "${var.environment}-${server.name}"
  }
}
```

## 11. Lọc bằng `for ... if`

```hcl
locals {
  enabled_servers = {
    for name, config in var.servers :
    name => config
    if config.enabled
  }
}
```

Kết hợp với `for_each`:

```hcl
resource "aws_instance" "server" {
  for_each = local.enabled_servers

  ami           = var.ami_id
  instance_type = each.value.instance_type

  tags = merge(local.common_tags, {
    Name = each.key
  })
}
```

## 12. Dynamic block

`for` expression tạo collection; `dynamic` tạo nhiều nested block:

```hcl
dynamic "ingress" {
  for_each = var.ingress_rules

  content {
    description = ingress.value.description
    from_port   = ingress.value.port
    to_port     = ingress.value.port
    protocol    = "tcp"
    cidr_blocks = ingress.value.cidr_blocks
  }
}
```

Chỉ dùng `dynamic` khi nested block thực sự lặp lại. Lạm dụng dynamic làm cấu hình khó đọc.

## 13. Template directives

Trong chuỗi hoặc template:

```hcl
message = <<-EOT
  %{if var.environment == "production"}
  Production mode
  %{else}
  Non-production mode
  %{endif}

  %{for name in var.names}
  - ${name}
  %{endfor}
EOT
```

## 14. Chọn công cụ nào?

| Nhu cầu | Công cụ |
|---|---|
| Chọn một trong hai giá trị | Conditional expression |
| Bật/tắt một resource | `count = condition ? 1 : 0` |
| Tạo N resource gần giống | `count` |
| Tạo resource theo key riêng | `for_each` |
| Biến đổi collection | `for` expression |
| Lọc collection | `for ... if` |
| Tạo nested blocks | `dynamic` |

## Thực hành cuối chương: bật/tắt application bằng dữ liệu

### Bước 1 — Xác định input

`applications` phải là `map(object(...))`. Key là tên ứng dụng; value chứa
`enabled`, `image`, `replicas`, `container_port` và `service_port`.

### Bước 2 — Lọc input

Trong `locals`, tạo `enabled_applications` bằng `for ... if`.

Với ba key `frontend`, `api`, `worker` và `worker.enabled = false`, kết quả phải
chỉ còn hai key:

```text
frontend
api
```

Kiểm tra bằng `terraform console` từ root module:

```hcl
local.enabled_applications
keys(local.enabled_applications)
```

### Bước 3 — Tạo module instances

Dùng đúng một module block:

```hcl
for_each = local.enabled_applications
```

Trong block đó:

```text
each.key   → tên application
each.value → object cấu hình của application
```

### Bước 4 — Kiểm tra hành vi

Chạy plan với `worker.enabled = false`: không được thấy address chứa `worker`.
Đổi sang `true`: plan phải xuất hiện module instance `application["worker"]`.

Đổi lại `false`: Terraform sẽ đề xuất destroy instance của worker. Đây là hành
vi đúng vì key đã biến mất khỏi map dùng cho `for_each`.

## Tài liệu chính thức

- [Input variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Conditional expressions](https://developer.hashicorp.com/terraform/language/expressions/conditionals)
- [For expressions](https://developer.hashicorp.com/terraform/language/expressions/for)
- [`for_each`](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)
- [Dynamic blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)

