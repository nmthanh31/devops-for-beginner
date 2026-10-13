# Terraform Lab 3 — Atlantis Merge Request Workflow trên Kubernetes

## Mục tiêu

Lab này đưa Terraform vào quy trình review thực tế:

```text
branch → Merge Request → Atlantis plan → review → atlantis apply → verify → merge
```

Bạn phải tự làm được:

- lưu Terraform state bằng Kubernetes backend;
- cho Terraform trong Pod dùng Kubernetes ServiceAccount;
- cấu hình Atlantis nhận GitLab webhook và comment vào Merge Request;
- khai báo project, autoplan và workflow trong `atlantis.yaml`;
- xử lý plan failure, apply failure, lock và drift.

Chỉ dùng môi trường `stag` trên cluster Rancher/local. Không dùng `dev` và không tạo `prd` trong lab này.

Atlantis được bootstrap một lần bằng Helm. Sau đó Atlantis quản lý workload `tf-lab3-stag` bằng Terraform. Không cố dùng Terraform để cài chính Atlantis trong bài đầu tiên vì sẽ tạo vòng lặp bootstrap.

Thứ tự triển khai của lab là: viết Terraform → kiểm tra local → commit lên GitLab → bootstrap Atlantis → Atlantis apply lần đầu. Trước khi Atlantis chạy, không apply workload bằng máy cá nhân.

> Không commit GitLab token, webhook secret, kubeconfig, Terraform state hoặc Helm values có secret.

## Đề bài cụ thể

Bạn phải dùng Terraform để triển khai **một web application tên `web`** vào Kubernetes.

### Các resource Terraform bắt buộc

| Resource | Tên bắt buộc | Yêu cầu |
|---|---|---|
| Namespace | `tf-lab3-stag` | Terraform tự tạo, không tạo bằng `kubectl` |
| ConfigMap | `web-content` | Có key `index.html`, chứa nội dung HTML đơn giản |
| Deployment | `web` | Image `nginx:alpine`, replicas lấy từ biến, container port `80` |
| Service | `web` | Type `ClusterIP`, service port `80`, target port `80` |

Deployment phải mount `ConfigMap/web-content` vào file:

```text
/usr/share/nginx/html/index.html
```

Labels bắt buộc:

```text
app.kubernetes.io/name = web
app.kubernetes.io/part-of = tf-lab3
environment            = stag
```

Không tạo Ingress, LoadBalancer, HPA, Database hoặc Secret ứng dụng trong Lab3. Mục tiêu là kiểm tra Atlantis với một project nhỏ, dễ quan sát.

### Input bắt buộc

File `terraform.tfvars` của `env/stag` phải có tối thiểu:

```text
environment = "stag"
replicas    = 1
image       = "nginx:alpine"
```

Bạn có thể đặt tên biến khác, nhưng phải giữ được ba ý nghĩa trên. `namespace_name` nên được tạo từ project/environment, không hardcode lặp lại ở nhiều resource.

### Output bắt buộc

Terraform phải output được:

```text
namespace_name
deployment_name
service_name
replicas
```

### Thay đổi dùng để test Atlantis

Baseline trên `main` dùng `replicas = 1`. Merge Request đầu tiên chỉ được đổi:

```text
replicas = 1 → replicas = 2
```

Atlantis phải plan và apply đúng thay đổi này. Merge Request thứ hai đổi:

```text
image = "nginx:alpine" → image = "nginx:1.27-alpine"
```

Không sửa đồng thời backend, RBAC và workload trong hai Merge Request kiểm thử này.

## Kiến trúc đích

```text
GitLab Merge Request/comment
      │ HTTPS webhook: /events
      ▼
Public HTTPS URL hoặc tunnel
      ▼
Atlantis Pod/StatefulSet
  ├─ clone branch của Merge Request
  ├─ terraform plan/apply
  ├─ ServiceAccount + RBAC
  └─ persistent storage cho plan
      ├─ Kubernetes API: workload tf-lab3-stag
      └─ Kubernetes backend: Secret + Lease trong namespace atlantis
```

## Cấu trúc cần đạt

Bạn tự tạo các file Terraform; README chỉ đưa yêu cầu, không phải lời giải hoàn chỉnh.

```text
F/
├── atlantis.yaml
└── terraform/terraform-jun/lab3/
    ├── README.md
    ├── backend/stag.hcl
    ├── env/stag/
    │   ├── backend.tf
    │   ├── main.tf
    │   ├── outputs.tf
    │   ├── providers.tf
    │   ├── terraform.tfvars
    │   ├── terraform.tf
    │   └── variables.tf
    └── shared/
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── modules/application/
            ├── main.tf
            ├── variables.tf
            ├── outputs.tf
            └── terraform.tf
```

## Giai đoạn 0 — chuẩn bị

### Repository phải là GitLab của công ty

Lab3 dùng GitLab làm Git host. Kiểm tra remote trước khi push:

```bash
git remote -v
```

Remote phải trỏ tới dạng:

```text
https://gitlab.company.example/<group>/<project>.git
```

Nếu repository Lab3 là một project GitLab khác, đổi remote theo quy trình của công ty. Không dùng lẫn GitHub webhook với GitLab webhook cho cùng một Atlantis project.

Kiểm tra Git từ thư mục repository:

```bash
git status
git ls-files | grep -E '(^|/)(\.terraform/|.*\.tfstate($|\.)|.*\.tfplan$)'
```

Lệnh thứ hai không được in ra file generated hoặc state.

Kiểm tra cluster `stag`:

```bash
kubectl --kubeconfig=terraform/k8s-config/local-rancher.yaml config current-context
kubectl --kubeconfig=terraform/k8s-config/local-rancher.yaml get nodes
```

Context phải là `local`. Tạo namespace bootstrap:

```bash
kubectl --kubeconfig=terraform/k8s-config/local-rancher.yaml \
  create namespace atlantis
```

Nếu namespace đã có thì chỉ cần `get namespace atlantis`. Namespace `tf-lab3-stag` phải do Terraform tạo.

## Giai đoạn 1 — viết Terraform

### Backend

Trong `env/stag/backend.tf`, khai báo Kubernetes backend rỗng. Trong `backend/stag.hcl`, đặt:

```text
namespace     = atlantis
secret_suffix = lab3-stag
```

Không đặt kubeconfig path vào backend config. Khi chạy local, dùng `KUBE_CONFIG_PATH`; khi chạy trong Atlantis, dùng in-cluster authentication.

### Provider

`providers.tf` không được chứa đường dẫn Windows. Để provider tự nhận ServiceAccount khi chạy trong Pod.

Để kiểm tra local trước:

```bash
export KUBE_CONFIG_PATH="../../../../k8s-config/local-rancher.yaml"
export KUBE_CTX="local"
```

Không commit token, certificate hoặc kubeconfig vào Terraform code.

### Workload

Module application phải tạo đúng bốn resource sau:

- `kubernetes_namespace_v1` cho `tf-lab3-stag` ở root/shared module;
- `kubernetes_config_map_v1` tên `web-content` với key `index.html`;
- `kubernetes_deployment_v1` tên `web`, mount ConfigMap và chạy nginx;
- `kubernetes_service_v1` tên `web` kiểu `ClusterIP`.

Deployment phải có selector khớp labels của Pod. Service selector cũng phải trỏ đúng label `app.kubernetes.io/name=web`.

Root `env/stag` gọi shared module và một module application duy nhất. Không tạo riêng module frontend/api.

Chạy local:

```bash
cd terraform/terraform-jun/lab3/env/stag
terraform fmt -recursive ../..
terraform init -reconfigure \
  -backend-config=../../backend/stag.hcl \
  -backend-config=in_cluster_config=false \
  -backend-config=config_path="$KUBE_CONFIG_PATH" \
  -backend-config=config_context="$KUBE_CTX"
terraform validate
terraform plan
```

Ở giai đoạn này, plan phải hiển thị đúng bốn resource ứng dụng và namespace cần tạo. Đây là kết quả đúng. Chưa chạy `terraform apply` local; lần apply đầu tiên sẽ được thực hiện từ Merge Request bằng Atlantis.

## Giai đoạn 2 — migrate state (chỉ dùng nếu đã apply local)

Nếu bạn làm đúng lab và chưa apply local, hãy bỏ qua giai đoạn này. Backend Kubernetes sẽ bắt đầu với state rỗng và Atlantis sẽ ghi state sau lần apply đầu tiên.

Chỉ thực hiện migration nếu trước đó bạn đã apply workload bằng local backend:

1. backup state ra file ngoài Git;
2. xác nhận workload đang tồn tại;
3. chạy `terraform init -migrate-state`;
4. trả lời `yes` để copy state;
5. kiểm tra `terraform state list` không bị mất resource.

Kiểm tra state backend và lock:

```bash
kubectl --kubeconfig=../../../../k8s-config/local-rancher.yaml \
  -n atlantis get secrets

kubectl --kubeconfig=../../../../k8s-config/local-rancher.yaml \
  -n atlantis get leases
```

Kubernetes backend lưu state trong Secret và lock bằng Lease; identity chạy Terraform phải có quyền đọc/ghi chúng. [Terraform Kubernetes backend](https://developer.hashicorp.com/terraform/language/backend/kubernetes)

## Giai đoạn 3 — RBAC cho Atlantis

Tạo ServiceAccount `atlantis`, không dùng kubeconfig cá nhân. Cấp quyền tối thiểu cho:

- Secret và Lease trong namespace `atlantis`;
- Namespace để Terraform tạo/quản lý `tf-lab3-stag`;
- Deployment, ReplicaSet, Service, ConfigMap, Event và Pod cần cho workload.

Không dùng `cluster-admin` cho PASS cuối. Nếu dùng tạm để bootstrap, phải ghi lại và giảm quyền trước khi kết thúc.

Kiểm tra quyền:

```bash
kubectl auth can-i get secrets -n atlantis \
  --as=system:serviceaccount:atlantis:atlantis
kubectl auth can-i create leases.coordination.k8s.io -n atlantis \
  --as=system:serviceaccount:atlantis:atlantis
kubectl auth can-i create deployments.apps -n tf-lab3-stag \
  --as=system:serviceaccount:atlantis:atlantis
```

Phải có `yes` cho quyền cần thiết và ít nhất một `no` cho negative test ngoài scope.

## Giai đoạn 4 — `atlantis.yaml`

File phải nằm ở **root Git repository**, không nằm riêng trong `lab3`.

Project phải có `name: lab3-stag`, đúng `dir`, workspace `default`, autoplan và workflow init backend. Hoàn thiện khung sau:

```yaml
version: 3

projects:
  - name: lab3-stag
    dir: terraform/terraform-jun/lab3/env/stag
    workspace: default
    workflow: lab3-stag
    autoplan:
      enabled: true
      when_modified:
        - "**/*.tf"
        - "**/*.tfvars"
        - "../../shared/**/*.tf"
        - "../../backend/stag.hcl"
        - ".terraform.lock.hcl"

workflows:
  lab3-stag:
    plan:
      steps:
        - init:
            extra_args:
              - "-backend-config=../../backend/stag.hcl"
        - plan
    apply:
      steps:
        - apply
```

Nếu có `projects`, Atlantis cần project được khai báo rõ. Các path trong `when_modified` là tương đối với `dir`. [Atlantis repo-level config](https://www.runatlantis.io/docs/repo-level-atlantis-yaml.html)

## Giai đoạn 5 — bootstrap Atlantis bằng Helm

Đây là phần làm thủ công một lần:

```bash
helm repo add runatlantis https://runatlantis.github.io/helm-charts
helm repo update
helm show values runatlantis/atlantis > /tmp/atlantis-values-reference.yaml
```

Atlantis cần GitLab access token, webhook secret, URL public và repo allowlist. Nên dùng một GitLab service user riêng cho Atlantis để comment không xuất hiện dưới tài khoản cá nhân. Tạo values thật ở ngoài Git; chỉ commit file example không chứa secret.

Các key cần có về mặt ý tưởng:

```yaml
atlantisUrl: https://YOUR_PUBLIC_ATLANTIS_URL
orgAllowlist: gitlab.company.example/platform/devops-for-beginner

gitlab:
  user: YOUR_GITLAB_ATLANTIS_USER
  token: YOUR_GITLAB_ACCESS_TOKEN
  secret: YOUR_WEBHOOK_SECRET
  hostname: gitlab.company.example

serviceAccount:
  create: true
  name: atlantis

environment:
  KUBE_IN_CLUSTER_CONFIG: "true"
```

Đối chiếu `helm show values` vì key có thể thay đổi theo chart version. Atlantis có official Helm chart và cần allowlist để giới hạn repo. [Atlantis Deployment](https://www.runatlantis.io/docs/deployment)

Atlantis cần storage bền vững cho plan giữa plan và apply. Nếu mất workspace plan, phải chạy plan lại.

Cài đặt:

```bash
helm upgrade --install atlantis runatlantis/atlantis \
  --namespace atlantis \
  --values atlantis-values.local.yaml
```

Kiểm tra:

```bash
kubectl -n atlantis get pods,svc
kubectl -n atlantis logs statefulset/atlantis --tail=100
```

## Giai đoạn 6 — GitLab webhook

GitLab của công ty phải truy cập được URL HTTPS của Atlantis, đồng thời Atlantis phải gọi ngược được GitLab để clone repository và cập nhật Merge Request. Nếu cluster local không có LoadBalancer public, dùng Ingress hoặc HTTPS tunnel được công ty cho phép.

Nếu GitLab dùng chứng chỉ CA nội bộ, Atlantis phải được mount CA nội bộ qua cơ chế của Helm/chart. Không tắt SSL verification để chữa lỗi certificate.

Trong GitLab, mở **Project → Settings → Webhooks**:

- Payload URL: `https://YOUR_PUBLIC_ATLANTIS_URL/events`;
- Content type: `application/json`;
- Secret Token: trùng với Atlantis;
- events: Push events, Comments, Merge Request events;
- SSL verification: bật;
- Active: bật.

Dùng **Test** hoặc delivery log của GitLab để kiểm tra webhook. `/events` là bắt buộc. [Atlantis GitLab webhooks](https://www.runatlantis.io/docs/configuring-webhooks.html)

GitLab access token cho Atlantis cần scope `api` theo tài liệu Atlantis. Không paste token vào command line hoặc commit vào values file. [Atlantis GitLab credentials](https://www.runatlantis.io/docs/access-credentials.html)

## Giai đoạn 7 — Merge Request đầu tiên

Trước khi cài Atlantis, commit code Terraform, backend config và `atlantis.yaml` lên `main`. Commit này chỉ là baseline code, chưa có workload được apply.

Sau khi Atlantis đã Ready và webhook GitLab hoạt động, tạo branch:

```bash
git switch -c feat/lab3-scale-web
```

Ở Merge Request đầu tiên, thay đổi một thuộc tính nhỏ, ví dụ replicas từ `1` thành `2`. Vì state đang rỗng, plan sẽ tạo workload với replicas `2`; đây là lần bootstrap bằng Atlantis.

```bash
git add terraform/terraform-jun/lab3 atlantis.yaml
git commit -m "feat(lab3): scale web deployment"
git push -u origin feat/lab3-scale-web
```

Atlantis phải tự comment plan vào Merge Request. Nếu cần, comment:

```text
atlantis plan -p lab3-stag
```

Đọc plan và xác nhận namespace, Deployment và Service đúng với code. Sau review, comment vào Merge Request:

```text
atlantis apply -p lab3-stag
```

Apply xảy ra khi Merge Request còn mở; chỉ merge sau khi apply thành công:

```bash
kubectl -n tf-lab3-stag rollout status deployment/<deployment-name>
kubectl -n tf-lab3-stag get pods,svc
```

Sau khi Merge Request đầu tiên được merge, tạo Merge Request thứ hai để đổi image sang `nginx:1.27-alpine`. Lần này plan phải thể hiện update trên Deployment đã tồn tại, không phải create lại toàn bộ stack.

## Giai đoạn 8 — failure drills

Thực hiện từng bài, lưu evidence:

- **Plan failure:** sai tên variable/reference, sửa branch và push lại.
- **Apply failure:** image tag không tồn tại, quan sát apply fail rồi sửa.
- **Lock:** mở hai Merge Request cùng sửa `lab3-stag`, quan sát repository lock.
- **Drift:** `kubectl scale` ngoài Terraform rồi chạy `atlantis plan -p lab3-stag`.
- **Docs-only:** chỉ sửa README, xác nhận autoplan không chạy nếu pattern không match.

Không dùng `force-unlock` nếu chưa xác nhận process cũ không còn chạy.

## Evidence bắt buộc

```text
01-atlantis-pod-ready.txt
02-webhook-delivery.png
03-mr-plan.png
04-mr-apply.png
05-kubernetes-state-secret.txt
06-kubernetes-state-lease.txt
07-rbac-can-i.txt
08-failure-drill.md
09-final-no-changes.txt
```

Che token, certificate, kubeconfig và nội dung Terraform state trước khi lưu/chia sẻ evidence.

## Definition of Done

```text
[ ] Không có state/kubeconfig/generated files trong Git
[ ] Terraform local plan/apply/verify chạy được
[ ] State migrate vào Kubernetes Secret
[ ] Lease state lock tồn tại
[ ] Provider chạy bằng ServiceAccount trong Pod
[ ] RBAC có negative test
[ ] Atlantis Pod Ready và có storage
[ ] GitLab webhook delivery thành công
[ ] Merge Request tự nhận plan comment
[ ] Apply thực hiện bằng comment trên Merge Request
[ ] Workload Kubernetes cập nhật đúng
[ ] Đã xử lý một plan failure và một apply failure
[ ] Đã kiểm tra drift
[ ] Merge chỉ sau apply thành công
[ ] Plan cuối trả về No changes
```

## Tài liệu chính thức

- [Atlantis Deployment](https://www.runatlantis.io/docs/deployment)
- [Atlantis repo-level configuration](https://www.runatlantis.io/docs/repo-level-atlantis-yaml.html)
- [Atlantis GitLab credentials](https://www.runatlantis.io/docs/access-credentials.html)
- [Atlantis GitLab webhooks](https://www.runatlantis.io/docs/configuring-webhooks.html)
- [Atlantis webhook secrets](https://www.runatlantis.io/docs/webhook-secrets)
- [Terraform Kubernetes backend](https://developer.hashicorp.com/terraform/language/backend/kubernetes)
- [Kubernetes provider authentication](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/index)
