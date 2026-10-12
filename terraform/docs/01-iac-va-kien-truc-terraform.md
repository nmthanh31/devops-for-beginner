# 01. Infrastructure as Code và kiến trúc Terraform

> [← Quay lại mục lục](./terraform-overview.md)

## Cách học chương này

Đừng cố nhớ mọi thuật ngữ. Sau chương này bạn chỉ cần làm được hai việc:

1. Chỉ ra thành phần nào đọc code, thành phần nào gọi Kubernetes API và thành
   phần nào lưu ánh xạ resource.
2. Nhìn một dòng trong plan và nói nó sẽ tạo, sửa hay xóa gì.

Dùng `lab1/main.tf` làm ví dụ xuyên suốt. Chưa cần sửa code trong chương này.

## 1. Infrastructure as Code là gì?

Infrastructure as Code (IaC) là cách mô tả, tạo và thay đổi hạ tầng bằng mã nguồn có thể lưu trữ, review và chạy lại.

Không dùng IaC, một quy trình tạo máy chủ có thể là:

1. Đăng nhập cloud console.
2. Chọn region.
3. Tạo network và subnet.
4. Chọn image và kích thước máy.
5. Tạo security rule.
6. Ghi lại cấu hình bằng tài liệu thủ công.

Với Terraform, trạng thái mong muốn nằm trong code:

```hcl
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = {
    Name        = "web"
    Environment = var.environment
  }
}
```

Lợi ích chính:

- Có lịch sử thay đổi trong Git.
- Có thể review trước khi triển khai.
- Tạo lại môi trường theo cách nhất quán.
- Giảm thao tác thủ công khó kiểm chứng.
- Dễ tự động hóa bằng CI/CD.
- Có thể chuẩn hóa bằng module.

IaC không tự động bảo đảm cấu hình đúng hoặc an toàn. Code vẫn cần review, test, phân quyền và quản lý secrets.

## 2. Declarative và imperative

Một script imperative mô tả từng bước:

```text
Tạo network
Lấy network ID
Tạo subnet trong network
Nếu subnet đã có thì bỏ qua
```

Terraform mô tả trạng thái cuối:

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "application" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}
```

Tham chiếu `aws_vpc.main.id` cho Terraform biết subnet phụ thuộc vào VPC. Terraform tự xác định thứ tự.

## 3. Kiến trúc Terraform

```text
                       ┌──────────────────────┐
                       │ Configuration (.tf)  │
                       └──────────┬───────────┘
                                  │
                                  ▼
┌──────────────┐          ┌───────────────────┐
│ State/Backend│◄────────►│  Terraform Core   │
└──────────────┘          └─────────┬─────────┘
                                   │ plugin protocol
                  ┌────────────────┼────────────────┐
                  ▼                ▼                ▼
          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
          │ AWS Provider │ │Azure Provider│ │ K8s Provider │
          └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                 ▼                ▼                ▼
              AWS API         Azure API      Kubernetes API
```

### Terraform Core

Terraform Core là chương trình `terraform`. Nó:

- Đọc và kiểm tra HCL.
- Nạp variables và modules.
- Yêu cầu provider cung cấp schema.
- Đọc state và làm mới thông tin tài nguyên.
- Xây dựng dependency graph.
- Tính toán execution plan.
- Điều phối create, read, update và delete.
- Ghi state sau thao tác.

### Provider

Provider là plugin triển khai cách giao tiếp với một nền tảng. Terraform Core không biết trực tiếp cách tạo EC2, Azure VM hay Kubernetes Deployment.

Provider định nghĩa:

- Các resource type.
- Các data source.
- Schema và kiểu dữ liệu.
- Cách xác thực.
- Cách ánh xạ cấu hình sang API request.
- Cách đọc kết quả API về state.

### API của nền tảng

Terraform thường gọi API thay vì đăng nhập vào máy chủ qua SSH. API có thể là cloud API, Kubernetes API hoặc API của một dịch vụ SaaS.

### State và backend

State là dữ liệu ánh xạ giữa địa chỉ Terraform và ID thật. Backend quyết định state được lưu ở đâu và có được khóa khi cập nhật hay không.

## 4. Các giai đoạn khi chạy Terraform

Khi chạy `terraform plan`, Terraform thường thực hiện các bước khái niệm sau:

1. Đọc tất cả file `.tf` trong root module.
2. Nạp child modules.
3. Đánh giá variables, locals và expressions.
4. Đọc state từ backend.
5. Cấu hình provider.
6. Đọc trạng thái tài nguyên từ API.
7. Xây dựng dependency graph.
8. So sánh cấu hình mong muốn, state và thực tế.
9. Hiển thị kế hoạch create, update, replace hoặc destroy.

Khi chạy `terraform apply`, Terraform thực hiện plan đã duyệt, cập nhật state theo các thao tác thành công và báo lỗi nếu provider/API thất bại. Apply không bảo đảm rollback toàn bộ nếu lỗi xảy ra giữa chừng.

## 5. Terraform quản lý vòng đời tài nguyên

Một resource thường có vòng đời CRUD:

```text
Create ──► Read ──► Update ──► Delete
              ▲         │
              └─────────┘
```

Không phải thuộc tính nào cũng cập nhật tại chỗ. Một số thay đổi buộc provider phải thay thế resource:

```text
-/+ destroy and then create replacement
```

Ví dụ đổi thuộc tính bất biến của một cloud resource có thể tạo tài nguyên mới và xóa tài nguyên cũ.

## 6. Terraform không phải là gì?

Terraform không phải:

- Một cloud provider.
- Một tiến trình giám sát chạy liên tục.
- Công cụ cấu hình hệ điều hành chuyên sâu như Ansible.
- Hệ thống tự động bảo đảm zero downtime.
- Nơi an toàn mặc định để lưu secrets.

Terraform có thể phối hợp với các công cụ khác:

```text
Terraform  → tạo network, VM, cluster, database
Ansible    → cấu hình package và hệ điều hành trên VM
Kubernetes → duy trì container workload
Helm       → đóng gói ứng dụng Kubernetes
CI/CD      → kiểm tra và kích hoạt plan/apply
```

## 7. Multi-provider

Một cấu hình có thể dùng nhiều provider:

```text
AWS provider        → VPC, EKS, load balancer
Kubernetes provider → Namespace, Deployment, Service
Cloudflare provider → DNS record
GitHub provider     → Repository settings
```

Trong hệ thống lớn, nên cân nhắc tách network, cluster, application và DNS thành các state/lifecycle riêng để giảm phạm vi ảnh hưởng.

## Thực hành cuối chương: đọc một plan như kiến trúc sư

Đứng trong một root module đã `init`, chạy:

```powershell
terraform plan
```

Trong output, tìm và ghi lại:

| Câu hỏi | Ví dụ câu trả lời |
|---|---|
| Terraform address là gì? | `kubernetes_namespace_v1.example` |
| Provider nào xử lý? | `hashicorp/kubernetes` |
| API tạo đối tượng gì? | Kubernetes Namespace |
| Ký hiệu hành động là gì? | `+` nghĩa là create |
| Sau apply, ánh xạ lưu ở đâu? | Terraform state |

Hoàn thành chương khi bạn tự mô tả được:

```text
main.tf → Terraform Core → Kubernetes provider → Kubernetes API → state
```

Không cần apply chỉ để hoàn thành bài này.

## Tài liệu chính thức

- [What is Terraform?](https://developer.hashicorp.com/terraform/intro)
- [Providers](https://developer.hashicorp.com/terraform/language/providers)
- [Dependency graph](https://developer.hashicorp.com/terraform/internals/graph)

