# LAB 2 — Tổ chức Terraform theo module và môi trường với Kubernetes

> Đây là tài liệu hướng dẫn thực hành, **không phải lời giải hoàn chỉnh**.
> Bạn tự tạo các file `.tf`, hoàn thành những vị trí `TODO` và kiểm tra sau
> từng checkpoint.

---

## 1. Bối cảnh

Trong Lab 1, Namespace, Deployment và Service đang được viết chung trong một
file `main.tf`. Cách này phù hợp để làm quen Terraform nhưng sẽ khó quản lý khi:

- Có nhiều ứng dụng.
- Có nhiều môi trường như `dev`, `stg`, `prd`.
- Nhiều ứng dụng có cấu trúc Deployment và Service giống nhau.
- Mỗi môi trường cần Terraform state riêng.
- Một thay đổi cần được tái sử dụng ở nhiều môi trường.

Lab 2 sẽ tổ chức lại code theo mô hình:

```text
Environment root module
        │
        ▼
Shared platform module
        │
        ├── Namespace child module
        └── Application child module (for_each)
```

Lab sử dụng Kubernetes provider thay cho AWS provider. Cluster Kubernetes đóng
vai trò là cloud platform để bạn thực hành Infrastructure as Code.

---

## 2. Kiến thức cần luyện tập

Sau khi hoàn thành Lab 2, bạn cần giải thích được:

1. Root module và child module khác nhau như thế nào.
2. Cách khai báo `map(object(...))`.
3. Cách dùng `for expression` để lọc một map.
4. Ý nghĩa của `key => value`.
5. Cách dùng `for_each` với module.
6. Cách truyền input vào module và lấy output ra ngoài.
7. Cách Terraform tự suy luận dependency.
8. Vì sao provider chỉ nên được cấu hình ở root module.
9. Vì sao các môi trường nên có state riêng.
10. Quan hệ giữa Deployment selector, Pod label và Service selector.

---

## 3. Đề bài

Hãy viết Terraform để triển khai một mini application platform lên Kubernetes.

### 3.1. Yêu cầu về Namespace

Mỗi môi trường có một Namespace riêng:

| Môi trường | Namespace |
|---|---|
| Development | `tf-lab2-dev` |
| Staging | `tf-lab2-stg` |
| Production | `tf-lab2-prd` |

Namespace phải được tạo bởi một child module có tên `namespace`.

### 3.2. Yêu cầu về ứng dụng

Mỗi application được bật phải có:

- Một Kubernetes Deployment.
- Một Kubernetes ClusterIP Service.
- Số replica được nhận qua variable.
- Container image được nhận qua variable.
- Container port và Service port được nhận qua variable.
- Các label xác định project và environment.

### 3.3. Yêu cầu về bật/tắt ứng dụng

Các application được khai báo bằng một map. Chỉ application có:

```hcl
enabled = true
```

mới được tạo.

Ví dụ dữ liệu đầu vào của môi trường `dev`:

```hcl
applications = {
  frontend = {
    enabled        = true
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 80
  }

  api = {
    enabled        = true
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 8080
  }

  worker = {
    enabled        = false
    image          = "nginx:alpine"
    replicas       = 1
    container_port = 80
    service_port   = 8081
  }
}
```

Kết quả mong đợi:

```text
tf-lab2-dev
├── Deployment/frontend
├── Service/frontend-service
├── Deployment/api
└── Service/api-service
```

Không được tạo Deployment hoặc Service cho `worker`.

---

## 4. Cấu trúc thư mục cần tự tạo

```text
lab2/
├── .terraform-version
├── .gitignore
├── README.md
│
├── backend/
│   ├── dev.hcl
│   ├── stg.hcl
│   └── prd.hcl
│
├── shared/
│   ├── terraform.tf
│   ├── variables.tf
│   ├── locals.tf
│   ├── main.tf
│   ├── outputs.tf
│   │
│   └── modules/
│       ├── namespace/
│       │   ├── terraform.tf
│       │   ├── variables.tf
│       │   ├── main.tf
│       │   └── outputs.tf
│       │
│       └── application/
│           ├── terraform.tf
│           ├── variables.tf
│           ├── main.tf
│           └── outputs.tf
│
├── env/
│   ├── dev/
│   │   ├── backend.tf
│   │   ├── terraform.tf
│   │   ├── providers.tf
│   │   ├── variables.tf
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── terraform.tfvars
│   │
│   ├── stg/
│   │   └── cấu trúc tương tự dev
│   │
│   └── prd/
│       └── cấu trúc tương tự dev
│
└── templates/
    └── app-config.yaml.tftpl
```

### Vì sao không dùng symbolic link giống hình tham khảo?

Hình tham khảo dùng symbolic link từ `env/dev` đến các file trong `shared`.
Symbolic link có thể dùng được nhưng thường gây khó khăn trên Windows vì:

- Có thể cần Developer Mode hoặc quyền Administrator.
- Git trên Windows có thể checkout symlink không đúng như mong đợi.
- Người mới học khó xác định file thật nằm ở đâu.

Trong lab này, mỗi environment là một root module nhỏ và gọi:

```hcl
source = "../../shared"
```

Cách này vẫn tái sử dụng code mà không cần symbolic link.

---

## 5. Vai trò của từng thư mục

### `shared/`

Đây là platform module dùng chung. Nó chịu trách nhiệm:

- Tính tên Namespace.
- Tạo common labels.
- Lọc các application được bật.
- Gọi module Namespace.
- Gọi nhiều application module bằng `for_each`.

`shared/` không được chứa cấu hình kubeconfig cụ thể.

### `shared/modules/namespace/`

Child module chỉ chịu trách nhiệm tạo một Namespace.

### `shared/modules/application/`

Child module tạo một Deployment và một Service cho một application.

Module không được biết nó đang chạy ở `dev`, `stg` hay `prd` ngoài các giá trị
được truyền vào.

### `env/dev/`

Đây là root module của môi trường development. Nó chịu trách nhiệm:

- Cấu hình Kubernetes provider.
- Chỉ định kubeconfig và context.
- Nhận giá trị trong `terraform.tfvars`.
- Gọi shared platform module.
- Chọn backend/state của môi trường.

### `backend/`

Chứa backend configuration riêng cho từng môi trường.

### `templates/`

Dùng trong bài nâng cao để render nội dung ConfigMap bằng `templatefile()`.

---

## 6. Giai đoạn 0 — Kiểm tra môi trường

### 6.1. Kiểm tra Terraform

```powershell
terraform version
```

Ghi version đang sử dụng vào `.terraform-version`.

### 6.2. Kiểm tra kubeconfig

Kubeconfig dùng cho lab đang nằm tại:

```text
D:\Documents\F\terraform\local-rancher.yaml
```

Kiểm tra context:

```powershell
kubectl config get-contexts `
  --kubeconfig D:\Documents\F\terraform\local-rancher.yaml
```

Chọn context `local` hoặc `rancher` tùy cluster bạn muốn sử dụng.

Kiểm tra kết nối:

```powershell
kubectl get nodes `
  --kubeconfig D:\Documents\F\terraform\local-rancher.yaml `
  --context local
```

Chỉ tiếp tục khi `kubectl get nodes` thành công.

### 6.3. Tạo `.gitignore`

Tự thêm các loại file không được commit:

```text
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
state/
```

Không bỏ qua `.terraform.lock.hcl`; file lock nên được commit trong dự án thực tế.

---

## 7. Giai đoạn 1 — Module Namespace

Làm thư mục này trước:

```text
shared/modules/namespace/
```

### 7.1. `terraform.tf`

Nhiệm vụ:

- Khai báo `required_providers`.
- Provider source là `hashicorp/kubernetes`.
- Không viết block `provider "kubernetes"` trong child module.

Khung:

```hcl
terraform {
  required_providers {
    kubernetes = {
      source = "TODO"
    }
  }
}
```

Phân biệt:

- `required_providers`: module nói nó cần provider nào.
- `provider "kubernetes"`: cấu hình kết nối đến cluster; chỉ root module làm.

### 7.2. `variables.tf`

Khai báo hai variable:

| Variable | Type | Ý nghĩa |
|---|---|---|
| `name` | `string` | Tên Namespace |
| `labels` | `map(string)` | Labels của Namespace |

`labels` nên có default là map rỗng.

Khung:

```hcl
variable "name" {
  description = "TODO"
  type        = TODO
}

variable "labels" {
  description = "TODO"
  type        = TODO
  default     = TODO
}
```

### 7.3. `main.tf`

Tạo resource:

```text
kubernetes_namespace_v1.this
```

Bạn cần tự hoàn thành:

```hcl
resource "kubernetes_namespace_v1" "this" {
  metadata {
    name   = TODO
    labels = TODO
  }
}
```

Không viết trực tiếp:

```hcl
name = "tf-lab2-dev"
```

vì như vậy module không tái sử dụng được.

### 7.4. `outputs.tf`

Xuất tên Namespace từ resource vừa tạo.

Khung:

```hcl
output "name" {
  description = "TODO"
  value       = TODO
}
```

Output nên lấy từ resource, không nên trả thẳng `var.name`.

### Checkpoint 1

Bạn hoàn thành checkpoint khi:

- Module có đủ `terraform.tf`, `variables.tf`, `main.tf`, `outputs.tf`.
- Không có provider configuration trong module.
- Không hardcode tên Namespace.
- Output tham chiếu resource Namespace.

Chưa cần chạy `terraform plan`, vì module chưa được root module gọi.

---

## 8. Giai đoạn 2 — Module Application

Làm trong:

```text
shared/modules/application/
```

### 8.1. Thiết kế interface trước khi viết resource

Khai báo các input sau:

| Variable | Type | Ví dụ |
|---|---|---|
| `name` | `string` | `frontend` |
| `namespace` | `string` | `tf-lab2-dev` |
| `image` | `string` | `nginx:alpine` |
| `replicas` | `number` | `1` |
| `container_port` | `number` | `80` |
| `service_port` | `number` | `8080` |
| `labels` | `map(string)` | common labels |

Thêm validation cho `replicas`:

```text
replicas phải lớn hơn hoặc bằng 1
```

Thêm validation cho port:

```text
1 <= port <= 65535
```

Bạn cần tự tìm cú pháp `validation` trong Terraform variable.

### 8.2. Thiết kế labels

Deployment metadata có các common label.

Pod bắt buộc có thêm:

```hcl
app = var.name
```

Bạn có thể dùng `merge()`:

```hcl
merge(var.labels, {
  app = var.name
})
```

Hãy lưu map này trong `locals` hoặc dùng trực tiếp. Không lặp lại cùng biểu thức ở
quá nhiều nơi.

### 8.3. Deployment

Tạo:

```text
kubernetes_deployment_v1.this
```

Deployment cần có cấu trúc logic:

```text
metadata
└── name, namespace, labels

spec
├── replicas
├── selector.match_labels
└── template
    ├── metadata.labels
    └── spec.container
        ├── name
        ├── image
        └── port.container_port
```

Ba vị trí sau phải thống nhất:

```text
Deployment selector: app = frontend
Pod label:           app = frontend
Service selector:   app = frontend
```

Nếu selector không khớp Pod label:

- Deployment có thể không quản lý đúng Pod.
- Service không tìm thấy endpoint.

Khung định hướng, không phải lời giải:

```hcl
resource "kubernetes_deployment_v1" "this" {
  metadata {
    name      = TODO
    namespace = TODO
    labels    = TODO
  }

  spec {
    replicas = TODO

    selector {
      match_labels = TODO
    }

    template {
      metadata {
        labels = TODO
      }

      spec {
        container {
          name  = TODO
          image = TODO

          port {
            container_port = TODO
          }
        }
      }
    }
  }
}
```

### 8.4. Service

Tạo:

```text
kubernetes_service_v1.this
```

Yêu cầu:

- Tên: `<application-name>-service`.
- Namespace nhận từ variable.
- Loại Service: `ClusterIP`.
- Selector trỏ tới Pod của application.
- `port` nhận từ `service_port`.
- `target_port` nhận từ `container_port`.

Phân biệt:

```text
Client trong cluster
       │
       │ service_port, ví dụ 8080
       ▼
Kubernetes Service
       │
       │ target_port, ví dụ 80
       ▼
Container port 80
```

### 8.5. Output

Module cần output ít nhất:

- Deployment name.
- Service name.

Output phải lấy từ resource vừa tạo.

### Checkpoint 2

Bạn hoàn thành checkpoint khi:

- Module không hardcode application name hoặc Namespace.
- Selector Deployment, Pod label và Service selector khớp nhau.
- Port được truyền qua variable.
- Có validation cơ bản.
- Output tham chiếu resource thực.

---

## 9. Giai đoạn 3 — Shared platform module

Làm trong:

```text
shared/
```

Shared module kết nối các child module lại với nhau.

### 9.1. `terraform.tf`

Khai báo:

- Terraform version constraint.
- Kubernetes provider requirement.

Không cấu hình kubeconfig tại đây.

### 9.2. `variables.tf`

Khai báo:

```text
project_name : string
environment  : string
applications : map(object(...))
```

`environment` chỉ chấp nhận:

```text
dev
stg
prd
```

Gợi ý dùng:

```hcl
contains(["dev", "stg", "prd"], var.environment)
```

Type của `applications`:

```hcl
map(object({
  enabled        = bool
  image          = string
  replicas       = number
  container_port = number
  service_port   = number
}))
```

### 9.3. `locals.tf`

Tạo ba local value.

#### Tên Namespace

Công thức:

```text
<project_name>-<environment>
```

Ví dụ:

```text
tf-lab2-dev
```

#### Common labels

Kết quả mong muốn:

```hcl
{
  "managed-by" = "terraform"
  project      = "tf-lab2"
  environment  = "dev"
}
```

#### Enabled applications

Sử dụng:

```hcl
enabled_applications = {
  for name, config in var.applications :
  name => config
  if config.enabled
}
```

Cách đọc:

```text
for name, config in var.applications
```

Duyệt từng cặp key/value trong map.

```text
name => config
```

Đưa key và value vào map mới.

```text
if config.enabled
```

Chỉ giữ phần tử được bật.

Với dữ liệu đề bài, kết quả phải tương đương:

```hcl
{
  frontend = { ... }
  api      = { ... }
}
```

Không có `worker`.

### 9.4. `main.tf` — Gọi Namespace module

Gọi module:

```text
module.namespace
```

Truyền:

- Tên Namespace từ local value.
- Common labels.

### 9.5. `main.tf` — Gọi Application module

Chỉ viết một block module application và dùng:

```hcl
for_each = local.enabled_applications
```

Trong module block:

- `each.key` là application name.
- `each.value` là object cấu hình application.
- Namespace phải nhận từ `module.namespace.name`.

Không viết ba block riêng:

```text
module frontend
module api
module worker
```

Mục tiêu của bài là dùng một module block với `for_each`.

### Dependency tự động

Khi application nhận Namespace bằng:

```text
module.namespace.name
```

Terraform hiểu rằng Namespace phải được tạo trước application. Không cần thêm
`depends_on` thủ công trong trường hợp này.

### 9.6. `outputs.tf`

Xuất:

- Namespace name.
- Map Deployment name theo application.
- Map Service name theo application.

Vì module application sử dụng `for_each`, nó là một map module instance. Gợi ý
dùng một `for expression` khác để tạo output map.

### Checkpoint 3

Bạn hoàn thành checkpoint khi:

- Chỉ có một `module "application"` block.
- Module dùng `for_each`.
- `worker` bị loại trong local value.
- Application nhận Namespace qua module output.
- Shared module không chứa kubeconfig.

---

## 10. Giai đoạn 4 — Root module `env/dev`

Làm trong:

```text
env/dev/
```

### 10.1. `terraform.tf`

Khai báo:

- `required_version`.
- Kubernetes provider requirement.

### 10.2. `providers.tf`

Đây mới là nơi cấu hình kết nối Kubernetes.

Khai báo hai variable:

```text
kubeconfig_path
kube_context
```

Provider cần sử dụng hai giá trị này.

Đường dẫn tương đối từ `env/dev` đến kubeconfig hiện có là:

```text
../../../../local-rancher.yaml
```

Bạn có thể dùng `abspath()` để đổi đường dẫn tương đối thành tuyệt đối.

Khung:

```hcl
provider "kubernetes" {
  config_path    = TODO
  config_context = TODO
}
```

Không ghi token, password hoặc certificate trực tiếp trong file Terraform.

### 10.3. `variables.tf`

Root module cần khai báo các input sẽ đọc từ `terraform.tfvars`:

- `kubeconfig_path`.
- `kube_context`.
- `project_name`.
- `environment`.
- `applications`.

### 10.4. `main.tf`

Gọi shared module:

```hcl
module "platform" {
  source = "../../shared"

  project_name = TODO
  environment  = TODO
  applications = TODO
}
```

Không tạo Kubernetes resource trực tiếp trong `env/dev/main.tf`.

### 10.5. `terraform.tfvars`

Điền:

```text
kubeconfig_path
kube_context
project_name
environment
applications
```

Dùng dữ liệu application được cung cấp trong phần đề bài.

### 10.6. `outputs.tf`

Chuyển tiếp output từ:

```text
module.platform
```

ra root module.

### Checkpoint 4

Bạn hoàn thành checkpoint khi:

- Root module gọi được `../../shared`.
- Provider chỉ được cấu hình ở `env/dev`.
- `terraform.tfvars` không chứa resource block.
- `env/dev/main.tf` không tạo trực tiếp Namespace, Deployment hoặc Service.

---

## 11. Giai đoạn 5 — Backend và state riêng

### 11.1. Tại sao phải tách state?

Nếu `dev` và `prd` dùng chung state:

- Thao tác ở dev có thể ảnh hưởng production.
- Khó phân quyền.
- Khó xác định blast radius.
- Một lỗi state có thể ảnh hưởng nhiều môi trường.

### 11.2. Local backend cho bài lab

Trong `env/dev/backend.tf`, khai báo một `local` backend rỗng. Giá trị `path`
được truyền khi chạy `terraform init`.

File `backend/dev.hcl` cần chỉ định state path:

```text
../../state/dev/terraform.tfstate
```

Tương tự:

```text
../../state/stg/terraform.tfstate
../../state/prd/terraform.tfstate
```

Trong dự án thực tế, có thể thay local backend bằng S3, Azure Storage, GCS hoặc
HCP Terraform.

---

## 12. Giai đoạn 6 — Khởi tạo và kiểm tra dev

Di chuyển vào root module:

```powershell
cd D:\Documents\F\terraform\terraform-jun\lab2\env\dev
```

### 12.1. Format

```powershell
terraform fmt -recursive ../..
```

### 12.2. Init

```powershell
terraform init '-backend-config=../../backend/dev.hcl'
```

Nếu bạn thay đổi `source` của module, chạy lại `terraform init`.

### 12.3. Validate

```powershell
terraform validate
```

`validate` kiểm tra:

- Cú pháp HCL.
- Input module có khớp không.
- Resource argument có hợp lệ không.
- Reference có tồn tại không.

Nó chưa đảm bảo cluster có thể tạo resource thành công.

### 12.4. Plan

```powershell
terraform plan -out=dev.tfplan
```

Đọc plan, không chỉ nhìn dòng tổng kết. Kiểm tra:

- Namespace đúng tên.
- Chỉ có `frontend` và `api`.
- Không có `worker`.
- Image và replica đúng.
- Service port và target port đúng.

Kết quả mong đợi ở phần cơ bản:

```text
1 Namespace
2 Deployments
2 Services
----------------
5 resources to add
```

Nếu plan có 7 resource, có thể bạn đã làm thêm ConfigMap nâng cao.

### 12.5. Apply

Chỉ apply sau khi đã đọc plan:

```powershell
terraform apply dev.tfplan
```

---

## 13. Giai đoạn 7 — Kiểm tra bằng kubectl

Đặt biến PowerShell để lệnh ngắn hơn:

```powershell
$kubeconfig = 'D:\Documents\F\terraform\local-rancher.yaml'
```

Kiểm tra Namespace:

```powershell
kubectl --kubeconfig $kubeconfig get namespace tf-lab2-dev
```

Kiểm tra Deployment:

```powershell
kubectl --kubeconfig $kubeconfig `
  -n tf-lab2-dev get deployments
```

Kiểm tra Pod và label:

```powershell
kubectl --kubeconfig $kubeconfig `
  -n tf-lab2-dev get pods --show-labels
```

Kiểm tra Service:

```powershell
kubectl --kubeconfig $kubeconfig `
  -n tf-lab2-dev get services
```

Kiểm tra Service có endpoint hay không:

```powershell
kubectl --kubeconfig $kubeconfig `
  -n tf-lab2-dev get endpoints
```

Nếu Service không có endpoint, kiểm tra lại:

```text
Service selector == Pod label
```

Kiểm tra Terraform state:

```powershell
terraform state list
```

Địa chỉ resource phải có dạng gần giống:

```text
module.platform.module.application["frontend"]...
module.platform.module.application["api"]...
```

Tên trong dấu `[]` xuất hiện vì module sử dụng `for_each`.

---

## 14. Giai đoạn 8 — Các thí nghiệm bắt buộc

Mỗi thí nghiệm phải theo quy trình:

```text
Sửa tfvars → terraform plan → giải thích plan → apply nếu an toàn
```

### Thí nghiệm 1 — Scale Deployment

Đổi:

```text
frontend replicas: 1 → 2
```

Kỳ vọng:

- Terraform update Deployment.
- Không replace Namespace.
- Không tạo Service mới.

### Thí nghiệm 2 — Bật application

Đổi:

```text
worker enabled: false → true
```

Kỳ vọng:

- Xuất hiện module instance `application["worker"]`.
- Terraform tạo thêm một Deployment và một Service.

### Thí nghiệm 3 — Tắt application

Đổi lại:

```text
worker enabled: true → false
```

Kỳ vọng:

- Key `worker` biến mất khỏi `local.enabled_applications`.
- Terraform đề xuất destroy resource thuộc module instance `worker`.

Đây là hành vi bình thường: khi một key biến mất khỏi `for_each`, Terraform cho
rằng instance tương ứng không còn được mong muốn.

### Thí nghiệm 4 — Thêm application mới

Thêm key:

```text
admin
```

Không sửa module. Terraform phải tự tạo module instance mới dựa trên map.

### Thí nghiệm 5 — Kiểm tra idempotency

Sau khi apply thành công, chạy lại:

```powershell
terraform plan
```

Kỳ vọng:

```text
No changes
```

Nếu vẫn có thay đổi, tìm nguyên nhân trước khi tiếp tục.

---

## 15. Giai đoạn 9 — Staging và Production

Chỉ làm sau khi `dev` hoàn chỉnh.

Sao chép **cấu trúc root module**, không sao chép child module:

```text
env/dev → env/stg
env/dev → env/prd
```

Sau đó thay giá trị môi trường.

| Thuộc tính | dev | stg | prd |
|---|---:|---:|---:|
| Namespace suffix | `dev` | `stg` | `prd` |
| Frontend replicas | 1 | 2 | 2 |
| API replicas | 1 | 1 | 2 |
| Worker enabled | false | false | true |

Khởi tạo staging:

```powershell
cd ..\stg
terraform init '-backend-config=../../backend/stg.hcl'
terraform validate
terraform plan
```

Khởi tạo production:

```powershell
cd ..\prd
terraform init '-backend-config=../../backend/prd.hcl'
terraform validate
terraform plan
```

Không cần apply `stg` và `prd` nếu cluster local không đủ tài nguyên. Mục tiêu là
so sánh plan và xác nhận state được tách riêng.

---

## 16. Bài nâng cao — ConfigMap và templatefile

Chỉ làm khi phần cơ bản đã chạy ổn định.

Tạo:

```text
templates/app-config.yaml.tftpl
```

Nội dung có các placeholder:

```text
application name
environment
managed by
```

Dùng `templatefile()` trong shared module để render nội dung riêng cho từng
application.

Truyền nội dung đã render vào application module bằng variable:

```text
config_content
```

Application module tạo:

```text
kubernetes_config_map_v1
```

Sau đó chọn một trong hai mức:

1. Chỉ tạo ConfigMap và kiểm tra nội dung bằng `kubectl`.
2. Mount ConfigMap vào container tại `/etc/lab2/app.yaml`.

Nếu thêm ConfigMap cho hai application được bật, plan dev tăng từ 5 lên 7
resource.

---

## 17. Gợi ý xử lý lỗi

### `Module not installed`

Nguyên nhân: chưa chạy init hoặc vừa thay đổi module source.

```powershell
terraform init
```

### `Unsupported argument`

Kiểm tra tên input tại module call có giống variable trong child module không.

### `Reference to undeclared input variable`

Bạn sử dụng `var.xxx` nhưng chưa khai báo variable `xxx`.

### `Reference to undeclared module`

Bạn tham chiếu `module.xxx` nhưng module block có label khác.

### Kubernetes provider không đọc được kubeconfig

Kiểm tra:

- Đường dẫn kubeconfig.
- Context name.
- Quyền đọc file.
- `kubectl get nodes` có chạy được với cùng kubeconfig hay không.

### Deployment không có Pod Ready

Kiểm tra:

```powershell
kubectl --kubeconfig $kubeconfig `
  -n tf-lab2-dev describe pod <pod-name>
```

Sau đó kiểm tra:

- Image có pull được không.
- Container port.
- Node có đủ tài nguyên không.

### Service không có endpoint

So sánh:

```text
Service.spec.selector
Pod.metadata.labels
```

Hai map phải có cặp key/value khớp nhau.

### Terraform muốn destroy không mong muốn

Không apply ngay. Kiểm tra:

- Key trong `for_each` có bị đổi tên không.
- `enabled` có bị chuyển sang `false` không.
- Có đang chạy đúng environment directory không.
- Backend/state path có đúng không.

---

## 18. Tiêu chí chấm bài

### Phần cơ bản — 7 điểm

- Cấu trúc thư mục đúng: 1 điểm.
- Namespace module tái sử dụng được: 1 điểm.
- Application module tạo Deployment và Service: 2 điểm.
- Dùng `for expression` lọc `enabled`: 1 điểm.
- Dùng module `for_each`: 1 điểm.
- `terraform validate` và `plan` thành công: 1 điểm.

### Chất lượng — 2 điểm

- Có variable type, description và validation: 0.5 điểm.
- Không hardcode environment trong child module: 0.5 điểm.
- Labels và selector đúng: 0.5 điểm.
- Output rõ ràng: 0.5 điểm.

### Nâng cao — 1 điểm

Hoàn thành một trong các mục:

- ConfigMap từ template.
- Readiness/liveness probe.
- Resource request/limit.
- NetworkPolicy.

---

## 19. Checklist tự kiểm tra

- [ ] Tôi tự tạo cấu trúc thư mục.
- [ ] Child module không chứa provider configuration.
- [ ] Namespace không bị hardcode trong application module.
- [ ] Chỉ có một application module block trong shared module.
- [ ] Application module sử dụng `for_each`.
- [ ] `worker` không xuất hiện khi `enabled = false`.
- [ ] Deployment selector khớp Pod label.
- [ ] Service selector khớp Pod label.
- [ ] Dev, staging và production có state riêng.
- [ ] `terraform fmt -check -recursive` thành công.
- [ ] `terraform validate` thành công.
- [ ] Đã đọc kỹ `terraform plan` trước khi apply.
- [ ] Chạy lại plan sau apply nhận `No changes`.
- [ ] Đã chạy `terraform destroy` sau khi hoàn thành lab.

---

## 20. Câu hỏi báo cáo

Viết câu trả lời bằng lời của bạn, không chỉ chép định nghĩa:

1. Vì sao `shared` được coi là child module khi gọi từ `env/dev`?
2. `name => config` tạo ra giá trị gì?
3. `if config.enabled` được xử lý ở thời điểm nào?
4. Vì sao `for_each` giữ địa chỉ resource ổn định hơn `count` trong bài này?
5. Điều gì xảy ra trong state khi đổi key `frontend` thành `web`?
6. Vì sao truyền `module.namespace.name` tạo dependency?
7. Provider requirement và provider configuration khác nhau thế nào?
8. Vì sao child module không nên chứa kubeconfig path?
9. Vì sao mỗi môi trường cần backend/state riêng?
10. Vì sao một Service có thể tồn tại nhưng không có endpoint?

---

## 21. Dọn tài nguyên

Chỉ destroy environment mà bạn đã apply:

```powershell
terraform destroy
```

Sau đó kiểm tra:

```powershell
kubectl --kubeconfig $kubeconfig get namespace tf-lab2-dev
```

Không xóa state bằng tay trước khi chạy `terraform destroy`, vì Terraform sẽ
mất thông tin về các resource mà nó đang quản lý.

---

## 22. Tài liệu chính thức

- [Terraform modules](https://developer.hashicorp.com/terraform/language/modules)
- [Module block](https://developer.hashicorp.com/terraform/language/block/module)
- [for_each](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)
- [Expressions](https://developer.hashicorp.com/terraform/language/expressions)
- [Kubernetes provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)

