# Lab: định tuyến cảnh báo Falco theo Kubernetes namespace

Service Python hiện nhận event từ Falcosidekick, tra namespace qua Kubernetes API, lọc theo chính sách namespace và gửi message đã định dạng tới Telegram. Với thay đổi workload có trạng thái hội tụ (create/update/scale/restart/delete), service tiếp tục kiểm tra API để gửi thông báo thứ hai khi workload sẵn sàng, đã bị xóa, thất bại hoặc quá thời hạn. Các thao tác tức thời như đọc Secret/exec/port-forward được báo theo kết quả audit, không chờ trạng thái rollout.

```text
Falco → Falcosidekick → Python router → Telegram
                            ↑       └── theo dõi rollout qua Kubernetes API
                            └── lọc namespace qua Kubernetes API
```

Falco chịu trách nhiệm phát hiện thao tác audit. Python router chuẩn hóa/gửi alert; với workload có trạng thái điều khiển, router phân biệt “API đã nhận yêu cầu” với “thay đổi đã hội tụ”.

## 1. Trạng thái cluster đã kiểm tra

Các thông tin dưới đây được đọc từ kubeconfig mặc định và cluster tại thời điểm lập tài liệu:

| Thành phần | Trạng thái |
|---|---|
| Kubernetes context | `local` |
| Falco namespace | `falco` |
| Falco Helm release | `falco`, chart `falco-9.1.0`, app `0.44.1` |
| Falco DaemonSet | 6/6 pod Running |
| Falcosidekick Service | `falco-falcosidekick.falco.svc.cluster.local:2801` |
| Falcosidekick UI | `falco-falcosidekick-ui`, port `2802` |
| K8s Audit webhook | `falco-k8saudit-webhook`, NodePort `30007` |
| Alertmanager Service | `rancher-monitoring-alertmanager.cattle-monitoring-system.svc.cluster.local:9093` |
| Falco values | `setup/falco-values.yaml` |

Values hiện bật Falcosidekick webhook tới `falco-router.python-lab.svc.cluster.local:8080/falco/events` với mức tối thiểu `warning`. Telegram gửi trực tiếp từ Falcosidekick đã được tắt/comment để tránh gửi trùng; service Python gửi message tới Telegram bằng Kubernetes Secret.

## 2. Kết quả mong muốn

Khi Falco phát một event từ workload:

1. Event có namespace, tên rule, priority, thời gian và thông tin pod/resource nếu có.
2. Falcosidekick POST event tới service Python nội bộ.
3. Service tìm Namespace object trong cache được đồng bộ từ Kubernetes API.
4. Service chỉ chuyển tiếp namespace có label cho phép; lấy team từ label owner.
5. Service định dạng message ngắn gọn và gửi Telegram.
6. Riêng rollout restart, service tiếp tục kiểm tra trạng thái workload và gửi message hoàn tất/thất bại.
7. Namespace chưa bị đánh dấu bỏ qua vẫn nhận alert; không yêu cầu gắn label cho mọi namespace.

## 3. Quy ước label namespace

Thống nhất dùng label trên Kubernetes Namespace làm cấu hình sở hữu. Ví dụ:

```yaml
metadata:
  labels:
    security.falco.io/alerts: "enabled"
    security.falco.io/team: "payments"
```

Quy ước:

- `security.falco.io/alerts=enabled`: cho phép chuyển alert của namespace.
- `security.falco.io/team=payments`: team/owner dùng để định tuyến.
- Thiếu label `alerts`: mặc định không gửi tới receiver của ứng dụng; ghi metric/log bị lọc.
- Thiếu label `team`: vẫn chuyển alert tới receiver mặc định của Platform và ghi metric namespace chưa có owner.
- Namespace hệ thống được xử lý bằng allow/deny policy rõ ràng trong cấu hình service; không hardcode danh sách dài trong Falco rule.

Thử gắn nhãn trên namespace lab sau khi đã chọn namespace phù hợp:

```powershell
kubectl label namespace <TEN_NAMESPACE_LAB> `
  security.falco.io/alerts=enabled `
  security.falco.io/team=platform `
  --overwrite

kubectl get namespace <TEN_NAMESPACE_LAB> `
  -o jsonpath='{.metadata.labels.security\.falco\.io/alerts}{" "}{.metadata.labels.security\.falco\.io/team}{"`n"}'
```

Không áp dụng nhãn đại trà cho toàn bộ namespace trước khi kiểm tra chính sách lọc.

## 4. Kiểm tra trước khi viết service

Chạy các lệnh chỉ đọc sau bằng kubeconfig mặc định:

```powershell
kubectl config current-context
kubectl get nodes -o wide
kubectl get namespace --show-labels
kubectl -n falco get daemonset,pods,services
kubectl -n cattle-monitoring-system get services | Select-String 'alertmanager'
helm list -n falco
```

Xem event Falco gần nhất mà không đọc hay in toàn bộ Helm values (values hiện có chứa thông tin xác thực Telegram):

```powershell
kubectl -n falco logs daemonset/falco -c falco --since=10m
```

Khi kiểm tra JSON event, cần xác nhận có các trường tương ứng:

- `rule`, `priority`, `time`, `output`.
- `output_fields["ka.target.namespace"]` cho K8s Audit rule.
- `output_fields["k8s.ns.name"]` hoặc trường namespace tương ứng cho syscall/container event.
- Tên pod/resource có thể nằm trong `ka.target.name`, `k8s.pod.name`, hoặc trường phù hợp với source.

Falco JSON output chỉ có các `output_fields` liên quan đến event/rule. Nếu namespace không có trong JSON, chỉnh output của rule đó để tham chiếu field namespace, ví dụ:

```yaml
output: >
  K8S EXEC |
  namespace=%ka.target.namespace |
  pod=%ka.target.name |
  direct_user=%ka.user.name
```

Điều này chỉ bổ sung dữ liệu event; không dùng namespace để nhân bản detection rule. Với K8s Audit, field hiện thấy trong values là `ka.target.namespace`. Với event syscall/container, field thường là `k8s.ns.name`. Hãy dựa trên JSON thực tế thay vì giả định hai source dùng cùng tên field.

## 5. Cấu trúc service Python đề xuất

Tạo các file trong `python/lab/`:

```text
python/lab/
├── README.md
├── pyproject.toml
├── app/
│   └── falco_router/
│       ├── __init__.py
│       ├── main.py             # FastAPI endpoints và lifecycle
│       ├── settings.py         # Cấu hình bằng environment variables
│       ├── event_parser.py     # Chuẩn hóa event Falco thành model nội bộ
│       ├── namespace_cache.py  # List/watch namespace và cache label
│       ├── policy.py           # Allow/deny và quyết định team
│       ├── alertmanager.py     # Gửi Alertmanager API v2
│       └── observability.py    # Logging và metrics
├── deploy/
│   ├── namespace.yaml
│   ├── rbac.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── network-policy.yaml
└── tests/
    ├── test_event_parser.py
    ├── test_policy.py
    └── test_alertmanager.py
```

### 5.1 Webhook nhận event

Tạo endpoint `POST /falco/events` nhận JSON từ Falcosidekick. Endpoint cần:

- Giới hạn kích thước request và kiểm tra schema tối thiểu.
- Trả `2xx` khi event đã được xử lý hoặc đưa vào hàng đợi nội bộ.
- Trả lỗi có thể retry khi chưa xử lý được; không trả `2xx` rồi làm mất event.
- Không ghi token, secret, header nhạy cảm hoặc toàn bộ payload chứa dữ liệu nhạy cảm vào log.
- Có `GET /healthz` và `GET /readyz`; readiness chỉ thành công khi service đã đồng bộ cache namespace và Alertmanager endpoint đã được cấu hình.

### 5.2 Chuẩn hóa namespace

Parser nên thử các field theo thứ tự phù hợp với source, ít nhất:

```text
output_fields["ka.target.namespace"]
output_fields["k8s.ns.name"]
```

Parser phải giữ lại event gốc để điều tra, nhưng model chuyển tiếp cần trường ổn định:

```text
namespace, rule, priority, timestamp, output, pod, source, cluster
```

Không parse chuỗi `output` bằng regex làm nguồn dữ liệu chính nếu có thể lấy namespace từ `output_fields`; format output có thể thay đổi.

### 5.3 Đồng bộ Kubernetes API

Service chạy trong cluster bằng ServiceAccount riêng. Dùng Kubernetes Python client để:

1. `list` Namespace khi khởi động, tạo cache tên namespace → labels.
2. `watch` Namespace để cập nhật cache khi label hoặc namespace thay đổi.
3. Tự list lại và nối watch sau khi watch hết hạn/mất kết nối.
4. Không gọi API `get namespace` cho từng event.

Namespace là resource cấp cluster, vì vậy dùng `ClusterRole` chỉ có quyền đọc `namespaces`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: falco-namespace-router
rules:
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list", "watch"]
```

Bind role này chỉ cho ServiceAccount của router. Không cấp quyền đọc Secrets, Pods hoặc quyền ghi cluster.

Nếu API chưa sẵn sàng, cache chưa đồng bộ hoặc namespace không tìm thấy, gửi alert vào tuyến mặc định kèm label `namespace="unknown"` khi không có tên namespace; đồng thời tăng metric lỗi. Không loại bỏ alert do lỗi tra cứu API.

### 5.4 Quyết định lọc và gán owner

Luồng policy đề xuất:

```text
Không lấy được namespace → chuyển tuyến Platform mặc định
Namespace không tồn tại trong cache → chuyển tuyến Platform mặc định
alerts != enabled → bỏ qua theo chính sách, ghi metric và log lý do
alerts == enabled, thiếu team → chuyển tuyến Platform mặc định
alerts == enabled, có team → gửi với label team đó
```

Chỉ `alerts != enabled` mới là quyết định lọc có chủ ý. Lỗi API, parser hoặc Alertmanager là lỗi pipeline, cần retry/metric/alert riêng chứ không coi là namespace bị tắt.

### 5.5 Alertmanager API

Service gửi alert đến:

```text
http://rancher-monitoring-alertmanager.cattle-monitoring-system.svc.cluster.local:9093/api/v2/alerts
```

Alert mẫu sau chuẩn hóa:

```json
[
  {
    "labels": {
      "alertname": "FalcoRuntimeEvent",
      "source": "falco",
      "cluster": "local",
      "namespace": "payments",
      "team": "payments",
      "severity": "warning",
      "rule": "VNPost K8s Human User Exec Pod"
    },
    "annotations": {
      "summary": "Falco phát hiện hành vi trong payments",
      "description": "Nội dung event đã được làm sạch trước khi gửi"
    },
    "startsAt": "2026-10-20T00:00:00Z",
    "endsAt": "2026-10-20T00:05:00Z"
  }
]
```

Thời gian trong ví dụ chỉ minh họa; code phải lấy timestamp từ event, chuẩn hóa UTC và đặt thời hạn alert theo cấu hình. Dùng label ổn định để Alertmanager gom nhóm; để pod, command và các chi tiết biến động trong annotation để hạn chế cardinality.

Mapping priority cần thống nhất, ví dụ `Critical → critical`, `Warning/Error → warning`, `Notice/Informational → info`. Chọn ngưỡng cảnh báo ở một nơi có chủ đích; hiện Falcosidekick Telegram đang đặt `minimumpriority: warning`.

## 6. Nối Falcosidekick tới service

Falcosidekick đang ở namespace `falco`, còn service lab nên chạy trong namespace riêng, ví dụ `python-lab`. DNS service dự kiến:

```text
falco-namespace-router.python-lab.svc.cluster.local:8080
```

Trong `setup/falco-values.yaml`, bổ sung output webhook dưới `falcosidekick.config`, đồng thời giữ nguyên cấu hình Telegram hiện tại trong giai đoạn kiểm thử:

```yaml
falcosidekick:
  config:
    webhook:
      address: http://falco-namespace-router.python-lab.svc.cluster.local:8080/falco/events
      method: POST
      minimumpriority: warning
```

Không thay thế các key đang có dưới `falcosidekick.config`; merge block `webhook` vào cấu hình hiện hữu. Xác nhận tên key với chart version `9.1.0` trước khi upgrade. Falcosidekick hỗ trợ generic webhook output; Falco chart kết nối Falco với Falcosidekick qua HTTP JSON output. [Falcosidekick Helm values](https://github.com/falcosecurity/charts/blob/master/charts/falcosidekick/values.yaml), [Falco Helm values](https://github.com/falcosecurity/charts/blob/master/charts/falco/values.yaml)

Không upgrade Falco release cho tới khi:

- Service Python đã chạy và readiness thành công.
- Webhook endpoint truy cập được từ pod Falcosidekick.
- RBAC, cache namespace và cấu hình Alertmanager đã sẵn sàng.
- Có kế hoạch rollback values.

## 7. Alertmanager grouping và routing

Alertmanager phải nhận labels `namespace` và `team` từ service. Cấu hình nguyên tắc:

```yaml
route:
  receiver: falco-platform-default
  group_by: [cluster, namespace, alertname, severity]
  group_wait: 10s
  group_interval: 2m
  repeat_interval: 4h
  routes:
    - receiver: falco-team-payments
      matchers:
        - source="falco"
        - team="payments"

    - receiver: falco-team-platform
      matchers:
        - source="falco"
        - team="platform"
```

`group_by` làm alert của mỗi namespace thành nhóm riêng. Matcher `team` chọn receiver. Route gốc là fallback cho namespace chưa ánh xạ. Alertmanager dừng ở route con đầu tiên khớp nếu `continue` không bật. [Alertmanager routing configuration](https://prometheus.io/docs/alerting/latest/configuration/)

Cluster đang dùng Rancher Monitoring. Trước khi sửa, xác định cấu hình Alertmanager hiện được quản lý bởi Helm values, AlertmanagerConfig CRD hay cơ chế GitOps của cluster. Không sửa trực tiếp Secret do operator quản lý nếu nguồn cấu hình là custom resource/Helm; thay đổi có thể bị operator ghi đè.

## 8. Triển khai workload

Service nên được chạy trong namespace `python-lab` với:

- Deployment 2 replicas khi chuyển sang dùng thật; lab có thể bắt đầu 1 replica.
- Service ClusterIP port `8080`, không tạo NodePort hoặc Ingress công khai.
- ServiceAccount và RBAC chỉ đọc Namespace.
- Resource requests/limits, startup/readiness/liveness probes.
- NetworkPolicy chỉ cho Falcosidekick gọi endpoint; cho router egress tới Kubernetes API và Alertmanager.
- Cấu hình endpoint, cluster name, timeout và policy qua ConfigMap/environment.
- Không đưa Telegram token, kubeconfig hay credential vào image, Git hoặc README.

## 9. Thứ tự thực hiện lab

1. **Baseline:** xác nhận kube context `local`, Falco/Falcosidekick/Alertmanager đang Ready và chọn namespace lab.
2. **Event schema:** thu một event an toàn từ rule K8s Audit hiện có và lưu fixture đã loại bỏ thông tin nhạy cảm vào `tests/fixtures/`.
3. **Python parser:** viết model và parser cho cả `ka.target.namespace` và `k8s.ns.name`; thêm unit test cho field thiếu/sai kiểu.
4. **Policy thuần:** viết hàm nhận namespace labels và trả `drop`, `platform-default` hoặc `team`; test từng nhánh.
5. **Namespace cache:** triển khai list/watch, xử lý reconnect và readiness; kiểm tra RBAC bằng `kubectl auth can-i`.
6. **Alertmanager client:** POST API v2, timeout, retry có backoff và metric lỗi; test bằng mock trước.
7. **HTTP service:** triển khai `/falco/events`, `/healthz`, `/readyz`; chạy local với event fixture.
8. **Kubernetes manifests:** tạo namespace `python-lab`, ServiceAccount, ClusterRole/Binding, Deployment và ClusterIP Service.
9. **Canary:** bật nhãn cho một namespace thử nghiệm; bật Falcosidekick webhook nhưng giữ Telegram hiện tại để đối chiếu.
10. **Xác nhận:** kiểm tra router nhận event, policy chọn đúng team, Alertmanager thấy label, receiver đúng và không có alert rơi mất.
11. **Cutover:** sau khi xác nhận, quyết định giữ Telegram trực tiếp hay chuyển Telegram thành receiver của Alertmanager. Tránh bật cả hai đường gửi cùng lúc nếu không muốn nhận tin trùng.
12. **Rollback:** tắt Falcosidekick webhook trong values để quay về luồng Telegram hiện tại; router có thể scale về 0 sau khi xác nhận không còn event cần xử lý.

## 10. Theo dõi thay đổi workload

Audit event chỉ chứng minh yêu cầu đã được Kubernetes API chấp nhận. Nó không chứng minh workload đã sẵn sàng. Service vì vậy gửi message yêu cầu trước, sau đó poll workload mỗi 5 giây (tối đa 10 phút):

- Deployment: generation đã được controller quan sát, đủ `updatedReplicas` và `availableReplicas`; `ProgressDeadlineExceeded` được báo thất bại.
- StatefulSet: đủ replicas đã update (tôn trọng rolling partition) và ready.
- DaemonSet: đủ node đã update và available; ReplicaSet: đủ replicas ready.
- Pod: trạng thái Running/Ready hoặc Succeeded; Failed được báo thất bại.
- Job: chờ Complete hoặc Failed. CronJob chỉ xác nhận cấu hình lịch đã được API lưu; không đợi lần chạy kế tiếp.
- Delete: xác nhận resource không còn tồn tại qua Kubernetes API.

ServiceAccount cần quyền `get` với `pods`, `deployments`, `statefulsets`, `daemonsets`, `replicasets` và `jobs` trong ClusterRole, ngoài quyền đọc Namespace sẵn có. Manifest `deploy/rbac.yaml` đã khai báo các quyền chỉ đọc cần thiết. Nếu trạng thái không hoàn tất trong 10 phút, service gửi thông báo timeout. Việc theo dõi đang giữ trong bộ nhớ của một replica; nếu pod router restart giữa lúc workload đang đổi, notification thứ hai có thể không được gửi.

Các rule thao tác workload/resource cần output `ka.verb`, `ka.user.name`, `ka.impuser.name` và `ka.response.code` để message có action, người thực hiện và kết quả API. `CLUSTER_NAME` trong Deployment quyết định tên cluster hiển thị trên Telegram.

## 10. Kiểm tra nghiệm thu

| Ca kiểm tra | Kết quả mong đợi |
|---|---|
| Namespace có `alerts=enabled`, team `payments` | Alert có `namespace`/`team` đúng và tới receiver Payments |
| Namespace bật nhưng thiếu team | Alert tới Platform default và có metric unknown owner |
| Namespace không bật alerts | Bị lọc có chủ đích; metric tăng; log có namespace và lý do |
| Event thiếu namespace | Không crash; đi tới default với namespace unknown |
| Namespace mới tạo hoặc đổi label | Cache cập nhật qua watch; quyết định policy dùng label mới |
| Kubernetes API tạm lỗi | Không làm process chết; dùng cache gần nhất và cảnh báo lỗi đồng bộ |
| Alertmanager tạm lỗi | Có retry/backoff hoặc queue; không trả thành công giả |
| Falcosidekick gọi endpoint | Nhận HTTP 2xx sau khi event đã được xử lý/đưa vào queue |
| Alert lặp cùng nhóm | Alertmanager gom theo `cluster, namespace, alertname, severity` |

## 11. Bảo mật và vận hành

- File `setup/falco-values.yaml` hiện có Telegram bot token dạng plaintext. Không chép token vào README, output lệnh, fixture hoặc Git diff; nên thu hồi/rotate token và chuyển sang Kubernetes Secret/External Secrets trước khi tiếp tục chia sẻ file values.
- Dùng TLS hoặc xác thực nội bộ nếu webhook vượt khỏi network boundary tin cậy. Tối thiểu giới hạn bằng NetworkPolicy.
- Namespace labels quyết định nơi nhận cảnh báo; kiểm soát ai có quyền sửa labels này bằng RBAC và quy trình review.
- Ghi metrics: số event nhận, số event chuyển tiếp, số event bị lọc, namespace chưa có owner, lỗi Kubernetes API, lỗi Alertmanager, queue/retry.
- Không coi Alertmanager là kho lưu trữ đầy đủ mọi event runtime. Nếu cần audit/điều tra dài hạn, lưu event gốc vào log backend riêng; Alertmanager chỉ phục vụ notification và grouping.
- Thêm giới hạn request, timeout, retry có backoff, chống payload quá lớn và log không chứa secret.

## 12. Tham khảo chính thức

- [Falco rule output](https://falco.org/docs/concepts/rules/basic-elements/)
- [Falco output channels và JSON fields](https://falco.org/docs/concepts/outputs/channels/)
- [Falcosidekick Helm values](https://github.com/falcosecurity/charts/blob/master/charts/falcosidekick/values.yaml)
- [Falco Helm chart values](https://github.com/falcosecurity/charts/blob/master/charts/falco/values.yaml)
- [Kubernetes API list/watch](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Alertmanager routing](https://prometheus.io/docs/alerting/latest/configuration/)

## 13. Rule hiện đang được tinh chỉnh

Trong `setup/falco-values.yaml`, custom rules được chia thành ba nhóm để alert có scope rõ và tránh trùng:

- `VNPost K8s Human User Workload Change`: create/update/patch/delete workload namespaced như Pod, Deployment, StatefulSet, DaemonSet, ReplicaSet, Job và CronJob. Rule riêng cho scale và rollout restart tiếp tục xử lý các thao tác đó.
- `VNPost K8s Human User Resource Change`: các resource namespaced còn lại, ví dụ Service, ConfigMap, Ingress, NetworkPolicy, Role/RoleBinding và thay đổi Secret.
- `VNPost K8s Human User Cluster Resource Change`: một allowlist resource cấp cluster có tác động cao như Namespace, Node, PersistentVolume, ClusterRole/Binding, CRD và StorageClass. Các API resource cluster-scope khác, trong đó có `selfusers`, không bị báo bởi rule generic.

Các output của rule được rút gọn về hành động, object, namespace/scope và status. Alert namespaced yêu cầu `ka.target.namespace exists`, nên không còn ghép chuỗi `namespace=<NA>` vào các thay đổi cấp cluster. Rule cluster-scope hiển thị `scope=cluster`.

### Giới hạn format Telegram hiện tại

Cluster đang chạy Falcosidekick `2.32.0`. Telegram output của phiên bản này dùng mẫu dựng sẵn gồm Time, Source, Hostname, Tags, toàn bộ `OutputFields` và `Output`; Telegram config không có tùy chọn để ẩn riêng khối Fields. Vì vậy rút gọn Falco `output` làm phần cuối tin nhắn ngắn hơn, nhưng **chưa loại được danh sách Fields tự động**.

Để tin Telegram thực sự chỉ còn vài dòng, cần chuyển việc gửi Telegram qua formatter riêng (service Python) hoặc dùng template notification ở Alertmanager. Formatter nên ưu tiên `impersonatedUser.extra.username[0]` khi có, nếu không dùng `ka.user.name`; hiển thị `action`, `resource/object`, `namespace` hoặc `scope=cluster`, và `status`. Không gửi `OutputFields` thô hoặc command đầy đủ trừ rule tương tác cần thiết. Giữ raw Falco event trong log/backend để điều tra.

Trước khi loại một resource khỏi rule, xác nhận event gốc và `requestURI`; danh sách cluster-scope là allowlist có chủ đích để giảm nhiễu, nên các resource mới phải được review rồi mới thêm.
