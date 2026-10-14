# Atlantis trên Kubernetes - Lab 3

Tài liệu này hướng dẫn cài đặt, cấu hình, kiểm tra và chạy thử Atlantis với
GitLab nội bộ và provider Kubernetes. Các lệnh bên dưới viết cho Git Bash.

## 1. Atlantis làm gì?

Luồng hoạt động:

~~~text
GitLab Merge Request
        | webhook /events
        v
Atlantis trên Kubernetes
        | terraform plan/apply
        v
Kubernetes API của cluster local
~~~

Atlantis nhận sự kiện từ Merge Request, checkout code, chạy Terraform và
comment kết quả ngược lại vào Merge Request. Atlantis không phải GitLab Runner.

## 2. Các file

| File | Công dụng |
|---|---|
| values.example.yaml | Mẫu Helm values, không chứa secret |
| values.local.yaml | File local chứa PAT/secret, không commit |
| lab3-rbac.yaml | Quyền Kubernetes cho Atlantis |
| atlantis-apisix.yaml | Route APISIX cho URL /atlantis |
| atlantis-architecture.drawio | Sơ đồ kiến trúc |

File values.atlantis.yaml đã được xóa vì có thể chứa credential thật.

## 3. Điều kiện cần

~~~bash
kubectl version --client
helm version
terraform version
git --version
~~~

Đặt biến dùng chung:

~~~bash
export KC="D:/Documents/F/terraform/k8s-config/local-rancher.yaml"
export ATLANTIS_DIR="D:/Documents/F/terraform/atlantis"
export HELM_CONFIG_HOME="D:/Documents/F/.helm"

kubectl --kubeconfig="$KC" config current-context
kubectl --kubeconfig="$KC" get nodes
~~~

Không commit kubeconfig vào Git. Thư mục k8s-config phải được ignore.

## 4. Chuẩn bị Helm chart

~~~bash
mkdir -p "$HELM_CONFIG_HOME"
helm repo add runatlantis https://runatlantis.github.io/helm-charts
helm repo update
helm search repo runatlantis/atlantis
~~~

Nếu repo đã tồn tại, warning từ helm repo add có thể bỏ qua.

## 5. Tạo values local

~~~bash
cd "$ATLANTIS_DIR"
cp values.example.yaml values.local.yaml
~~~

Mở values.local.yaml và thay placeholder:

~~~yaml
orgAllowlist: "scm.vnpost.vn/thanhnm1/atlantis-test"

atlantisUrl: "https://dev-cmp-api.vnpost.vn/atlantis"

gitlab:
  user: "atlantis"
  token: "<PAT-cua-GitLab>"
  secret: "<webhook-secret>"
  hostname: "scm.vnpost.vn"
~~~

Quy tắc:

- orgAllowlist có dạng hostname/group/project, không có https:// và không có .git.
- atlantisUrl là URL người dùng/GitLab dùng để truy cập Atlantis.
- gitlab.token là PAT của user/service account Atlantis để clone repo và
  comment vào Merge Request.
- gitlab.secret là chuỗi tự đặt, phải giống Secret Token trong GitLab Webhook.
- gitlab.hostname chỉ là hostname GitLab.

Không ghi PAT hoặc webhook secret vào values.example.yaml.

Giữ các thiết lập lab sau:

~~~yaml
service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
webhook_ingress:
  enabled: false

enableKubernetesBackend: true

serviceAccount:
  create: true
  name: atlantis

replicaCount: 1

volumeClaim:
  enabled: true
  dataStorage: 1Gi
  accessModes: ["ReadWriteOnce"]

sharePlanDirVolumeClaim:
  enabled: false
~~~

Cluster này dùng APISIX, không dùng Ingress Nginx của chart Atlantis. Vì vậy
giữ ingress.enabled: false và webhook_ingress.enabled: false.

## 6. Cài đặt hoặc cập nhật Atlantis

Từ thư mục D:/Documents/F:

~~~bash
cd /d/Documents/F

helm upgrade --install atlantis runatlantis/atlantis \
  --namespace atlantis \
  --create-namespace \
  --kubeconfig="$KC" \
  --values "$ATLANTIS_DIR/values.local.yaml"
~~~

Kiểm tra:

~~~bash
helm --kubeconfig="$KC" -n atlantis status atlantis
kubectl --kubeconfig="$KC" -n atlantis get pods,svc,pvc
kubectl --kubeconfig="$KC" -n atlantis logs pod/atlantis-0 --tail=100
~~~

Trạng thái đúng là pod 1/1 Running, Service ClusterIP, PVC Bound.

## 7. Cấp quyền Kubernetes

Sau khi Helm tạo ServiceAccount:

~~~bash
kubectl --kubeconfig="$KC" apply -f "$ATLANTIS_DIR/lab3-rbac.yaml"

kubectl --kubeconfig="$KC" auth can-i create deployments.apps \
  --namespace=tf-lab3-stag \
  --as=system:serviceaccount:atlantis:atlantis
~~~

Kết quả cần là yes. File RBAC chỉ phục vụ lab; production cần giới hạn quyền
theo namespace và resource.

## 8. Smoke test bằng port-forward

~~~bash
kubectl --kubeconfig="$KC" -n atlantis port-forward svc/atlantis 4141:80
~~~

Ở terminal khác:

~~~bash
curl http://localhost:4141/healthz
~~~

Kết quả đúng:

~~~json
{"status":"ok"}
~~~

Mở giao diện tại http://localhost:4141. Port-forward chỉ để kiểm tra local;
GitLab server không thể gọi webhook vào localhost của máy bạn.

## 9. Publish qua APISIX

File atlantis-apisix.yaml cấu hình:

~~~text
https://dev-cmp-api.vnpost.vn/atlantis
~~~

Route dùng plugin proxy-rewrite để bỏ prefix /atlantis trước khi chuyển request
vào Atlantis, vì Atlantis phục vụ UI ở /.

Apply và kiểm tra:

~~~bash
kubectl --kubeconfig="$KC" apply -f "$ATLANTIS_DIR/atlantis-apisix.yaml"
kubectl --kubeconfig="$KC" -n atlantis get apisixroute atlantis
kubectl --kubeconfig="$KC" -n ingress-apisix get apisixtls atlantis
curl -k -i https://dev-cmp-api.vnpost.vn/atlantis/healthz
~~~

Endpoint phải trả HTTP 200 và {"status":"ok"}. Không bật Ingress Nginx của
chart trong cluster này; APISIX mới là gateway đang phục vụ domain.

## 10. Tạo GitLab Webhook

Trong project GitLab:

~~~text
Settings -> Webhooks -> Add new webhook
~~~

Điền:

~~~text
URL:
https://dev-cmp-api.vnpost.vn/atlantis/events

Secret Token:
giá trị gitlab.secret trong values.local.yaml
~~~

Bật Push events, Comments, Merge request events và Enable SSL verification.

Bấm Test -> Merge request events và cần nhận HTTP 200.

GitLab Self-Managed có thể chặn webhook tới IP private. Nếu nhận lỗi
URL is blocked hoặc Host cannot be resolved or invalid, GitLab Admin phải
allowlist dev-cmp-api.vnpost.vn:443 trong Admin -> Settings -> Network ->
Outbound requests. Đây là chính sách mạng của GitLab.

## 11. Chạy thử bằng Merge Request

Repo thử nghiệm:

~~~text
scm.vnpost.vn/thanhnm1/atlantis-test
~~~

~~~bash
cd /d/Projects/atlantis-test
git switch main
git pull
git switch -c test/atlantis-plan
~~~

Sửa một thay đổi nhỏ trong env/stag/terraform.tfvars, ví dụ nội dung HTML của
ConfigMap:

~~~bash
git add env/stag/terraform.tfvars
git commit -m "test: trigger atlantis plan"
git push -u origin test/atlantis-plan
~~~

Tạo Merge Request từ test/atlantis-plan vào main. Atlantis có thể tự chạy plan
vì autoplan.enabled: true. Nếu không, comment trong MR:

~~~text
atlantis plan
~~~

Kết quả xuất hiện trong Overview -> Activity dưới dạng comment của Atlantis,
không nằm trong tab Pipelines. Sau khi review, chạy:

~~~text
atlantis apply
~~~

Kiểm tra resource:

~~~bash
kubectl --kubeconfig="$KC" -n tf-lab3-stag get deployment,service,configmap
~~~

## 12. Cấu hình atlantis.yaml của repo

Repo atlantis-test dùng project:

~~~yaml
version: 3

projects:
  - name: lab3-stag
    dir: env/stag
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
~~~

## 13. Xử lý lỗi thường gặp

### Không có comment Atlantis

Kiểm tra Webhook -> Recent events, sau đó:

~~~bash
kubectl --kubeconfig="$KC" -n atlantis logs pod/atlantis-0 --tail=200
~~~

Nếu log không có event, GitLab chưa gọi được Atlantis. Nếu có URL is blocked,
xử lý allowlist mạng GitLab.

### Repository is not allowed

Kiểm tra chính xác:

~~~yaml
orgAllowlist: "scm.vnpost.vn/thanhnm1/atlantis-test"
~~~

### HTTP 503

~~~bash
kubectl --kubeconfig="$KC" -n atlantis get pod,svc,endpoints atlantis
kubectl --kubeconfig="$KC" -n atlantis describe pod atlantis-0
~~~

Nếu APISIX báo no valid upstream node, kiểm tra EndpointSlice và chờ
controller đồng bộ. Không bật Ingress Nginx để sửa lỗi này.

### HTTP 404 ở /atlantis/

Apply lại route và kiểm tra plugin proxy-rewrite:

~~~bash
kubectl --kubeconfig="$KC" apply -f "$ATLANTIS_DIR/atlantis-apisix.yaml"
~~~

### Backend Terraform lỗi

Atlantis phải chạy trong namespace atlantis và ServiceAccount phải có quyền
đọc/ghi Kubernetes Secret state của Lab3. Kiểm tra RBAC trước khi apply.

## 14. Dọn lab

Chỉ chạy khi chắc chắn muốn xóa Atlantis:

~~~bash
helm --kubeconfig="$KC" uninstall atlantis -n atlantis
kubectl --kubeconfig="$KC" delete namespace atlantis
~~~

Các lệnh trên xóa release và PVC trong namespace atlantis; không chạy trong lúc
đang có plan/apply.
