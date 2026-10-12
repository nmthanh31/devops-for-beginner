# 07. Dependency, lifecycle, import và refactoring

> [← Quay lại mục lục](./terraform-overview.md)

## Cách học chương này

Tập trung vào hai tình huống đang có trong Lab 2:

1. Application phải đợi Namespace vì nhận `module.namespace.name`.
2. Rancher tự thêm annotation vào Namespace, gây plan lặp lại nếu không xử lý
   lifecycle phù hợp.

Import và refactoring là phần sau; đừng thử trên state đang dùng nếu chưa sao lưu.

## 1. Dependency graph

Terraform không thực thi resource theo thứ tự file hoặc thứ tự dòng. Nó xây dựng một đồ thị phụ thuộc.

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "application" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}
```

Tham chiếu `aws_vpc.main.id` tạo dependency ngầm:

```text
aws_vpc.main ──► aws_subnet.application
```

Terraform tạo VPC trước subnet và thường xóa theo thứ tự ngược lại.

## 2. Dependency ngầm và dependency tường minh

### Dependency ngầm

Ưu tiên tham chiếu giá trị thật:

```hcl
network_id = module.network.network_id
```

Ưu điểm:

- Dễ hiểu nguyên nhân phụ thuộc.
- Terraform biết chính xác dữ liệu được truyền.
- Graph ít bảo thủ hơn.

### `depends_on`

Chỉ dùng khi dependency tồn tại về hành vi nhưng không thể hiện qua dữ liệu:

```hcl
resource "some_resource" "application" {
  depends_on = [some_resource.policy]
}
```

Lạm dụng `depends_on` có thể làm plan có nhiều unknown values và giảm khả năng chạy song song.

## 3. Unknown values

Một số thuộc tính chưa thể biết trước apply:

```text
id = (known after apply)
```

Terraform vẫn có thể truyền unknown value qua dependency graph. Nhưng các giá trị quyết định số lượng hoặc key của resource, như `for_each`, thường phải biết trước khi tạo tài nguyên.

Ví dụ dễ lỗi:

```hcl
for_each = toset(aws_instance.web[*].id)
```

Các ID do API tạo chưa biết tại thời điểm plan. Nên dùng key từ input đã biết trước.

## 4. Lifecycle mặc định

Provider quyết định một thay đổi có thể update tại chỗ hay phải replace.

Plan có thể hiển thị:

```text
~ update in-place
-/+ destroy and then create replacement
```

Replacement có thể gây downtime, đổi IP, hostname hoặc ID. Luôn đọc thuộc tính nào `forces replacement` trong plan/provider docs.

## 5. `create_before_destroy`

```hcl
resource "some_resource" "application" {
  # ...

  lifecycle {
    create_before_destroy = true
  }
}
```

Terraform cố tạo resource thay thế trước rồi mới xóa resource cũ. Điều này chỉ hoạt động khi:

- API cho phép hai tài nguyên cùng tồn tại.
- Tên/địa chỉ không xung đột.
- Quota đủ.
- Dependency cho phép chuyển đổi an toàn.

Nó không tự động bảo đảm zero downtime.

## 6. `prevent_destroy`

```hcl
resource "some_database" "production" {
  # ...

  lifecycle {
    prevent_destroy = true
  }
}
```

Terraform từ chối plan muốn destroy resource khi block này còn trong cấu hình. Đây là lớp bảo vệ bổ sung, không thay thế backup, IAM và quy trình phê duyệt.

Nếu xóa cả resource block khỏi cấu hình thì Terraform không còn đọc lifecycle trong block đó; cần thiết kế quy trình bảo vệ ở cấp backend, policy và platform.

## 7. `ignore_changes`

```hcl
lifecycle {
  ignore_changes = [
    tags["UpdatedBy"],
  ]
}
```

Dùng khi một hệ thống khác được chủ ý cho phép quản lý một thuộc tính. Rủi ro:

- Che drift quan trọng.
- Làm code không còn phản ánh đầy đủ thực tế.
- Khó xác định owner của thuộc tính.

Không dùng `ignore_changes = all` như cách sửa nhanh mọi khác biệt.

## 8. `replace_triggered_by`

Một resource có thể cần replace khi resource hoặc thuộc tính khác thay đổi:

```hcl
lifecycle {
  replace_triggered_by = [
    some_resource.configuration,
  ]
}
```

Chỉ dùng khi replacement là yêu cầu thiết kế rõ ràng.

## 9. Import tài nguyên có sẵn

Viết resource block tương ứng:

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "existing-company-logs"
}
```

Import bằng CLI:

```powershell
terraform import aws_s3_bucket.logs existing-company-logs
```

Hoặc dùng import block:

```hcl
import {
  to = aws_s3_bucket.logs
  id = "existing-company-logs"
}
```

Sau import:

1. Chạy `terraform plan`.
2. Bổ sung code cho khớp cấu hình thực tế mong muốn.
3. Không apply mù nếu plan đề xuất thay đổi hoặc xóa thuộc tính quan trọng.

Import tạo binding trong state; nó không tự động chứng minh resource block đã mô tả đầy đủ và đúng ý định.

## 10. Đổi tên resource bằng `moved`

Nếu đổi:

```hcl
resource "aws_s3_bucket" "old_name" {}
```

thành:

```hcl
resource "aws_s3_bucket" "logs" {}
```

Nếu không báo cho Terraform, plan có thể hiểu là xóa resource cũ và tạo resource mới. Khai báo:

```hcl
moved {
  from = aws_s3_bucket.old_name
  to   = aws_s3_bucket.logs
}
```

`moved` block cũng hữu ích khi chuyển resource vào module.

## 11. Ngừng quản lý mà không xóa

Đây là thao tác cần review kỹ. Với cấu hình phù hợp, `removed` block có thể ghi rõ ý định:

```hcl
removed {
  from = aws_s3_bucket.logs

  lifecycle {
    destroy = false
  }
}
```

Sau apply, Terraform bỏ binding khỏi state nhưng không xóa remote object. Lệnh `terraform state rm` cũng có thể làm Terraform quên resource, nhưng thay đổi state trực tiếp và nên được dùng thận trọng.

## 12. `-target` không phải workflow bình thường

```powershell
terraform plan -target=<address>
```

`-target` hữu ích trong tình huống khôi phục đặc biệt, nhưng có thể tạo thay đổi một phần và bỏ qua phần còn lại của cấu hình. Sau khi dùng, luôn chạy một plan đầy đủ.

## 13. Checklist khi refactor

- Xác định resource address trước và sau.
- Dùng `moved` block khi đổi tên/chuyển module.
- Không để hai address cùng sở hữu một remote object.
- Review plan không có destroy ngoài ý muốn.
- Sao lưu/version state.
- Không chạy refactor đồng thời với apply khác.
- Chạy plan đầy đủ sau thay đổi.

## Thực hành cuối chương: dependency và Rancher drift

### Phần 1 — Chứng minh dependency

Trong shared module, application nhận:

```hcl
namespace = module.namespace.name
```

Chạy `terraform graph` hoặc đọc plan. Namespace phải được tạo trước Deployment
và Service dù block module Namespace nằm ở file khác. Không cần `depends_on`
thủ công vì reference đã tạo dependency ngầm.

### Phần 2 — Bỏ qua annotation do Rancher quản lý

Nếu plan lặp lại việc xóa `cattle.io/*` hoặc `lifecycle.cattle.io/*`, thêm vào
resource Namespace:

```hcl
lifecycle {
  ignore_changes = [
    metadata[0].annotations
  ]
}
```

Sau đó chạy:

```powershell
terraform fmt
terraform validate
terraform plan
```

Kết quả mong đợi là `No changes` nếu không có thay đổi khác.

Chỉ dùng `ignore_changes` cho thuộc tính thật sự do hệ thống khác sở hữu. Không
dùng nó để che mọi drift hoặc bỏ qua thay đổi quan trọng.

### Phần 3 — Quan sát address trước khi refactor

```powershell
terraform state list
```

Ghi lại address trước khi đổi tên resource/module. Nếu address thay đổi, Terraform
có thể hiểu là destroy object cũ và create object mới; khi đó cần cân nhắc
`moved` block.

## Tài liệu chính thức

- [Dependency graph](https://developer.hashicorp.com/terraform/internals/graph)
- [Lifecycle meta-argument](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)
- [Import](https://developer.hashicorp.com/terraform/language/import)
- [Refactoring](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [Remove resources](https://developer.hashicorp.com/terraform/language/resources/syntax#removing-resources)

