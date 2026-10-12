# 02. Ngôn ngữ HCL căn bản

> [← Quay lại mục lục](./terraform-overview.md)

HCL là ngôn ngữ cấu hình mà Terraform sử dụng. HCL được thiết kế để con người dễ đọc, nhưng vẫn hỗ trợ kiểu dữ liệu, biểu thức, hàm và tham chiếu.

## Cách học chương này

Mở `terraform-jun/lab1/main.tf` trong lúc đọc. Với mỗi ví dụ, hãy tìm một cấu
trúc tương tự trong Lab 1. Sau chương này bạn phải phân biệt được:

- Block với argument.
- String, number, bool, list và map.
- Giá trị hardcode với reference như `var.name` hoặc `resource.type.attribute`.

Không cần thuộc cú pháp; cần biết nhìn lỗi và xác định kiểu dữ liệu đang sai.

## 1. Argument và block

Argument gán một giá trị:

```hcl
region = "ap-southeast-1"
```

Block chứa một nhóm cấu hình:

```hcl
resource "aws_s3_bucket" "logs" {
  bucket_prefix = "company-logs-"

  tags = {
    Environment = "development"
  }
}
```

Phân tích block trên:

| Thành phần | Giá trị | Ý nghĩa |
|---|---|---|
| Block type | `resource` | Khai báo tài nguyên được quản lý |
| Label 1 | `aws_s3_bucket` | Resource type do provider định nghĩa |
| Label 2 | `logs` | Tên nội bộ trong module |
| Argument | `bucket_prefix` | Giá trị đầu vào cho resource |
| Argument | `tags` | Map được truyền cho resource |

Địa chỉ của resource là `aws_s3_bucket.logs`.

## 2. Kiểu dữ liệu cơ bản

```hcl
# String
name = "web-server"

# Number
replicas = 3

# Boolean
enabled = true

# Null: thường có nghĩa là không cung cấp argument tùy chọn
description = null
```

## 3. Collection và structural types

### List hoặc tuple

```hcl
availability_zones = [
  "ap-southeast-1a",
  "ap-southeast-1b",
]

first_zone = local.availability_zones[0]
```

### Set

Set không có thứ tự ổn định và loại bỏ giá trị trùng:

```hcl
toset(["web", "api", "web"])
```

### Map hoặc object

```hcl
tags = {
  Environment = "development"
  Team        = "platform"
}

server = {
  name          = "web"
  instance_type = "t3.micro"
  enabled       = true
}
```

Truy cập bằng `local.tags.Environment`, `local.tags["Team"]` hoặc `local.server.instance_type`.

## 4. String interpolation

Chèn biểu thức vào chuỗi:

```hcl
name = "${var.project_name}-${var.environment}"
```

Nếu cả giá trị chỉ là một tham chiếu thì viết trực tiếp:

```hcl
region = var.region
```

Không cần viết `region = "${var.region}"`.

## 5. Heredoc

Heredoc phù hợp với nội dung nhiều dòng như cloud-init hoặc policy:

```hcl
user_data = <<-EOT
  #!/bin/bash
  echo "hello" > /tmp/message.txt
EOT
```

## 6. Comments

```hcl
# Comment một dòng

// Cũng là comment một dòng

/*
  Comment
  nhiều dòng
*/
```

## 7. References

```hcl
var.region                                  # variable
local.name_prefix                          # local
aws_vpc.main.id                            # resource attribute
data.aws_caller_identity.current.account_id # data source
module.network.vpc_id                      # module output
aws_instance.web[0].id                     # resource dùng count
aws_instance.server["api"].id              # resource dùng for_each
```

## 8. Operators

```hcl
# So sánh
var.environment == "production"
var.replicas >= 2
var.name != ""

# Logic
var.enabled && var.environment == "production"
var.is_admin || var.is_operator
!var.disabled

# Số học
var.base_port + 1
var.node_count * 2
```

## 9. Functions

Terraform có nhiều hàm dựng sẵn:

```hcl
upper("web")                         # "WEB"
lower("API")                         # "api"
length(["a", "b"])                  # 2
join(",", ["a", "b"])              # "a,b"
split(",", "a,b")                   # ["a", "b"]
merge(local.common, local.extra)      # gộp map
lookup(local.sizes, "prod", "small") # đọc map có mặc định
try(var.config.name, "default")       # fallback khi biểu thức lỗi
coalesce(var.name, "default")         # giá trị đầu tiên không null/rỗng
```

## 10. File `.tf`

Terraform đọc mọi file `.tf` ở cấp cao nhất của thư mục module và ghép chúng thành một cấu hình logic. Nó không chạy `terraform.tf` trước `main.tf` hay `outputs.tf`.

```text
project/
├── terraform.tf
├── providers.tf
├── variables.tf
├── main.tf
└── outputs.tf
```

Việc chia file chỉ phục vụ khả năng đọc và bảo trì. Thư mục con không tự động được nạp; nó là module riêng nếu được gọi bằng `module` block.

## 11. Định dạng

```powershell
terraform fmt
terraform fmt -check -recursive
```

## Thực hành cuối chương: đọc HCL trong Lab 1

Mở `terraform-jun/lab1/main.tf` và tìm:

1. Một block `provider`.
2. Một block `resource`.
3. Một string.
4. Một number.
5. Một map labels.
6. Một nested block như `metadata`, `spec` hoặc `container`.

Sau đó chạy:

```powershell
terraform fmt -check
```

Nếu lệnh in tên file và trả lỗi, chạy `terraform fmt`, xem diff rồi chạy lại.

Thử biểu thức mà không tạo tài nguyên:

```powershell
terraform console
```

Nhập lần lượt:

```hcl
"tf-lab2-${"dev"}"
merge({ environment = "dev" }, { app = "frontend" })
contains(["dev", "stag"], "dev")
```

Kết quả lần lượt phải là một string, một map và `true`. Gõ `exit` để thoát.

## Tài liệu chính thức

- [HCL syntax](https://developer.hashicorp.com/terraform/language/syntax/configuration)
- [Types and values](https://developer.hashicorp.com/terraform/language/expressions/types)
- [Built-in functions](https://developer.hashicorp.com/terraform/language/functions)
- [Files and configuration structure](https://developer.hashicorp.com/terraform/language/files)

