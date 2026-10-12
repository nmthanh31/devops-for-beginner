# BÁO CÁO GIẢI PHÁP ĐỊNH TUYẾN CẢNH BÁO FALCO THEO NAMESPACE

**Phạm vi:** Cụm Kubernetes tập trung tại môi trường DEV và Staging  
**Ngày báo cáo:** 09/10/2026  
**Đơn vị thực hiện:** ........................................................  
**Người thực hiện:** ........................................................

## Tóm tắt điều hành

Báo cáo đề xuất cơ chế tiếp nhận và định tuyến cảnh báo bảo mật runtime do Falco phát hiện trên các cụm Kubernetes tập trung. Giải pháp chuẩn hóa trường namespace của sự kiện Falco thành label `namespace`, chuyển cảnh báo vào Alertmanager, sau đó dùng routing tree để phân phối đến đúng Sub Endpoint của đội vận hành. Sub Endpoint chịu trách nhiệm phân loại mức độ nghiêm trọng, chống gửi trùng, định dạng nội dung và chuyển tiếp đến Telegram hoặc webhook của từng đội.

Kiến trúc được khuyến nghị là **Falco → Falcosidekick hoặc lớp chuẩn hóa → Alertmanager → Sub Endpoint → Telegram và webhook**. Cách tổ chức này tách riêng ba trách nhiệm: Falco phát hiện hành vi; Alertmanager gom nhóm và định tuyến; Sub Endpoint áp dụng logic nghiệp vụ và tích hợp kênh thông báo. Cấu hình namespace và quyền sở hữu được quản lý bằng GitOps để hạn chế sai tuyến khi số lượng namespace tăng.

Báo cáo không giả định kết quả kiểm thử khi chưa có dữ liệu đo thực tế. Các chỉ tiêu độ trễ, tỷ lệ gửi thành công và tỷ lệ lọc trùng được trình bày dưới dạng tiêu chí nghiệm thu; đội triển khai sẽ cập nhật số liệu sau khi chạy kịch bản tại DEV và Staging.

## 1. Bối cảnh và yêu cầu

Falco theo dõi hoạt động runtime trên node và container, đối chiếu sự kiện hệ thống với bộ luật để phát hiện hành vi bất thường như mở shell tương tác trong container, ghi vào thư mục nhị phân, truy cập tệp nhạy cảm hoặc thực thi chương trình không mong đợi. Khi dùng cho nhiều cụm Kubernetes tập trung, một luồng cảnh báo chung dễ gây quá tải cho đội trực vận hành và làm chậm quá trình xác định đơn vị chịu trách nhiệm.

Yêu cầu của giải pháp gồm:

1. Phân tách cảnh báo theo namespace và cụm Kubernetes.
2. Chuyển cảnh báo về đúng đội phụ trách mà không phải cấu hình thủ công tại từng node.
3. Chuẩn hóa ba mức độ `Critical`, `Warning` và `Info`.
4. Giảm cảnh báo lặp lại nhưng không làm mất sự kiện khôi phục hoặc sự kiện có mức độ nghiêm trọng cao.
5. Hiển thị đủ thông tin để người trực xác định nhanh rule, namespace, pod, container, user, command và liên kết quan sát liên quan.
6. Hỗ trợ Telegram và webhook, có khả năng mở rộng thêm kênh trong tương lai.
7. Có số liệu theo dõi độ trễ, tỷ lệ gửi thành công, số cảnh báo bị lọc trùng và số cảnh báo không xác định được đội sở hữu.

## 2. Phạm vi

### 2.1 Trong phạm vi

- Sự kiện runtime do Falco phát hiện trong workload Kubernetes.
- Chuẩn hóa dữ liệu Falco thành alert tương thích Alertmanager.
- Định tuyến theo `cluster`, `namespace`, `severity` và `source`.
- Sub Endpoint nhận webhook từ Alertmanager.
- Lọc trùng, định dạng thông báo và gửi Telegram hoặc webhook.
- Kiểm thử trên DEV và Staging.
- Tài liệu cấu hình, vận hành, giám sát và xử lý sự cố.

### 2.2 Ngoài phạm vi

- Thiết kế hoặc hiệu chỉnh toàn bộ bộ luật Falco cho từng ứng dụng.
- Tự động cô lập pod, khóa tài khoản hoặc thực hiện phản ứng chủ động.
- Thay thế hệ thống SIEM hoặc kho lưu trữ log dài hạn.
- Cam kết SLA sản xuất trước khi hoàn thành đo tải và kiểm thử lỗi.

## 3. Nguyên tắc thiết kế

- **Tách trách nhiệm:** Falco phát hiện, Alertmanager định tuyến, Sub Endpoint thực hiện logic nghiệp vụ và tích hợp kênh.
- **Namespace là khóa sở hữu:** Mọi cảnh báo Kubernetes phải có label `namespace`; cảnh báo thiếu namespace được đưa về receiver mặc định của đội nền tảng.
- **Không tin cậy dữ liệu đầu vào:** Payload phải được kiểm tra schema, giới hạn kích thước và làm sạch nội dung trước khi tạo tin nhắn.
- **Idempotent:** Gửi lại cùng một webhook không tạo nhiều thông báo trong cửa sổ chống trùng.
- **Không mất cảnh báo:** Lỗi kênh đích phải được retry có backoff; khi vượt ngưỡng, sự kiện được đưa vào hàng đợi lỗi để xử lý lại.
- **Cấu hình bằng mã:** Bảng ánh xạ namespace và receiver, Alertmanager config, template và secret reference được quản lý qua GitOps.
- **Quan sát được:** Mỗi chặng có metric và log tương quan bằng `event_id` hoặc `fingerprint`.

## 4. Kiến trúc đề xuất

```text
Falco DaemonSet trên các node
            |
            | JSON qua HTTP
            v
Falcosidekick hoặc lớp chuẩn hóa sự kiện
            |
            | Alertmanager API v2
            v
Alertmanager HA
  - group theo cluster namespace alertname severity
  - route theo namespace
  - retry webhook
       |                 |                    |
       v                 v                    v
Sub Endpoint A     Sub Endpoint B      Sub Endpoint mặc định
       |                 |                    |
       +------ Telegram và webhook theo đội --+
```

### 4.1 Luồng xử lý

1. Falco sinh JSON event, bao gồm `rule`, `priority`, `time`, `source`, `hostname` và `output_fields`.
2. Falcosidekick hoặc lớp chuẩn hóa đọc `k8s.ns.name`, `k8s.pod.name` và thông tin container, sau đó tạo alert gửi đến Alertmanager.
3. Trường `k8s.ns.name` được chuẩn hóa thành label `namespace`; cụm nguồn được gắn label `cluster`.
4. Alertmanager gom nhóm cảnh báo theo các label ổn định và đi qua routing tree.
5. Receiver tương ứng gửi payload webhook đến Sub Endpoint của đội phụ trách.
6. Sub Endpoint xác thực yêu cầu, chuẩn hóa severity, tạo khóa chống trùng, định dạng nội dung và gửi đến kênh đích.
7. Metric và structured log được ghi cho toàn bộ kết quả nhận, bỏ trùng, gửi thành công, retry và lỗi cuối.

### 4.2 Lưu ý kỹ thuật đối với label Falco

Trong JSON Falco, namespace thường xuất hiện dưới khóa `output_fields["k8s.ns.name"]`. Falcosidekick chuyển ký tự không hợp lệ trong tên label Alertmanager thành dấu gạch dưới, vì vậy trường này có thể xuất hiện dưới dạng `k8s_ns_name`. Nếu yêu cầu routing bắt buộc dùng label `namespace`, lớp chuẩn hóa phải sao chép giá trị từ `k8s.ns.name` hoặc `k8s_ns_name` sang `namespace` trước khi gọi Alertmanager API.

Không nên đưa toàn bộ trường động như command line, process ID hoặc thời gian sự kiện vào tập label dùng để nhận diện alert. Những trường này có cardinality cao và làm giảm hiệu quả gom nhóm hoặc chống trùng. Chúng nên nằm trong `annotations`; label chỉ giữ các thuộc tính phục vụ định tuyến và nhận diện ổn định.

## 5. Thiết kế định tuyến cảnh báo

### 5.1 Bộ label tối thiểu

| Label | Nguồn | Mục đích | Bắt buộc |
|---|---|---|---|
| `source` | Giá trị cố định `falco` | Phân biệt cảnh báo Falco với Prometheus | Có |
| `cluster` | Cấu hình tại từng cụm | Xác định cụm phát sinh | Có |
| `namespace` | `k8s.ns.name` | Xác định đội sở hữu | Có với workload Kubernetes |
| `alertname` | Tên Falco rule | Gom nhóm và hiển thị | Có |
| `severity` | Ánh xạ từ Falco priority | Ưu tiên xử lý | Có |
| `pod` | `k8s.pod.name` | Điều tra nhanh | Nên có |
| `container` | Tên hoặc ID container | Điều tra nhanh | Nên có |
| `environment` | `dev`, `staging`, `prod` | Tách môi trường | Có |

Các trường như `proc_cmdline`, `user_name`, `image`, `node`, mô tả chi tiết và đường dẫn dashboard nên đặt trong annotations.

### 5.2 Ánh xạ mức độ nghiêm trọng

| Falco priority | Severity chuẩn hóa | Hành động đề xuất |
|---|---|---|
| `Emergency`, `Alert`, `Critical` | `critical` | Gửi ngay; gắn kênh trực; retry ưu tiên cao |
| `Error`, `Warning` | `warning` | Gửi theo nhóm nhỏ; đội dịch vụ xử lý trong ca trực |
| `Notice`, `Informational`, `Debug` | `info` | Gom nhóm; có thể chỉ gửi kênh theo dõi |

Việc ánh xạ phải được kiểm soát theo phiên bản. Với rule tùy chỉnh có tác động cao, có thể ghi đè severity theo tên rule thay vì chỉ dựa vào priority.

### 5.3 Cấu hình Alertmanager tham khảo

```yaml
route:
  receiver: falco-platform-default
  group_by: [cluster, namespace, alertname, severity]
  group_wait: 5s
  group_interval: 2m
  repeat_interval: 4h
  routes:
    - receiver: falco-platform-critical
      matchers:
        - source="falco"
        - severity="critical"
      continue: true

    - receiver: falco-team-payments
      matchers:
        - source="falco"
        - namespace=~"payments|billing"
      continue: false

    - receiver: falco-team-order
      matchers:
        - source="falco"
        - namespace=~"order|fulfillment"
      continue: false

receivers:
  - name: falco-team-payments
    webhook_configs:
      - url: https://alert-gateway.example.internal/hooks/payments
        send_resolved: true
        max_alerts: 50

  - name: falco-team-order
    webhook_configs:
      - url: https://alert-gateway.example.internal/hooks/order
        send_resolved: true
        max_alerts: 50

  - name: falco-platform-critical
    webhook_configs:
      - url: https://alert-gateway.example.internal/hooks/platform-critical
        send_resolved: true

  - name: falco-platform-default
    webhook_configs:
      - url: https://alert-gateway.example.internal/hooks/platform-default
        send_resolved: true
```

`continue: true` ở route critical cho phép vừa gửi đến đội sở hữu namespace, vừa gửi bản sao đến đội nền tảng hoặc SOC. Thứ tự route phải được kiểm thử vì Alertmanager dừng tại nhánh khớp đầu tiên khi `continue` bằng `false`.

### 5.4 Quản lý bảng ánh xạ namespace

Nên duy trì tệp cấu hình có cấu trúc rõ ràng:

```yaml
ownership:
  payments:
    namespaces: [payments, billing]
    endpoint: /hooks/payments
    telegram_secret_ref: secret/alerts/payments
  order:
    namespaces: [order, fulfillment]
    endpoint: /hooks/order
    telegram_secret_ref: secret/alerts/order
  platform:
    namespaces: [kube-system, monitoring, falco]
    endpoint: /hooks/platform
    telegram_secret_ref: secret/alerts/platform
```

Pipeline CI cần kiểm tra namespace trùng giữa các đội, endpoint không tồn tại, secret reference sai và namespace mới chưa có owner. Namespace chưa ánh xạ luôn đi về receiver mặc định thay vì bị loại bỏ.

## 6. Thiết kế Sub Endpoint

### 6.1 Chức năng

Sub Endpoint là dịch vụ HTTP stateless, chạy tối thiểu hai replica. Trạng thái chống trùng và retry được lưu ở Redis hoặc kho dùng chung để bảo đảm hoạt động đúng khi scale ngang.

Các bước xử lý một yêu cầu:

1. Xác thực nguồn gửi bằng mTLS hoặc header bí mật luân chuyển định kỳ.
2. Giới hạn kích thước request, timeout đọc và số lượng alert trong một batch.
3. Kiểm tra schema webhook Alertmanager và loại bỏ trường không cần thiết.
4. Xác định `team`, `namespace`, `severity` và trạng thái `firing` hoặc `resolved`.
5. Tạo fingerprint ổn định và thực hiện thao tác `SET NX EX` trên Redis.
6. Tạo thông báo theo template của kênh.
7. Gửi đến Telegram và webhook; retry với exponential backoff và jitter.
8. Trả HTTP 2xx chỉ khi request đã được ghi nhận bền vững hoặc xử lý thành công theo thiết kế hàng đợi.

### 6.2 Schema đầu vào tối thiểu

Sub Endpoint cần hỗ trợ payload webhook chuẩn của Alertmanager, gồm:

- `receiver`
- `status`
- `alerts[]`
- `groupLabels`
- `commonLabels`
- `commonAnnotations`
- `externalURL`

Mỗi phần tử `alerts[]` cần đọc `labels`, `annotations`, `startsAt`, `endsAt`, `generatorURL` và `fingerprint` nếu có.

### 6.3 Cơ chế chống trùng

Khóa chống trùng đề xuất:

```text
sha256(status | cluster | namespace | alertname | pod | container | severity)
```

Chính sách cửa sổ chống trùng:

| Severity | Cửa sổ đề xuất | Ghi chú |
|---|---:|---|
| `critical` | 5 phút | Không nén quá lâu; vẫn cho phép nhắc lại khi sự cố kéo dài |
| `warning` | 15 phút | Gom các sự kiện lặp trên cùng đối tượng |
| `info` | 30 phút | Hạn chế nhiễu cho kênh theo dõi |

Sự kiện `resolved` không bị bỏ chỉ vì trùng với `firing`; khi gửi resolved thành công, trạng thái active tương ứng được xóa hoặc đánh dấu kết thúc. Sub Endpoint nên lưu `duplicate_count` để tin nhắn tiếp theo có thể cho biết số lần lặp đã được nén.

Nếu Alertmanager retry cùng một request do timeout, Sub Endpoint phải trả lại kết quả an toàn mà không gửi lần hai. Fingerprint từ Alertmanager có thể được dùng làm idempotency key, nhưng vẫn cần phương án tự tính khi nguồn gửi không cung cấp trường này.

### 6.4 Retry và xử lý lỗi

- Retry lỗi mạng, HTTP `429` và `5xx` bằng exponential backoff có jitter.
- Không retry vô hạn với lỗi xác thực hoặc payload `4xx` không thể sửa.
- Tôn trọng `Retry-After` của kênh đích.
- Đưa sự kiện vượt số lần retry vào dead-letter queue.
- Cảnh báo nội bộ khi queue tăng, tỷ lệ lỗi vượt ngưỡng hoặc endpoint đích chậm.
- Không ghi bot token, secret header hoặc toàn bộ command nhạy cảm vào log.

## 7. Định dạng thông báo và tích hợp đa kênh

### 7.1 Mẫu thông báo Telegram

```text
🔴 FALCO CRITICAL

Rule: Terminal shell in container
Cluster: k8s-staging-01
Namespace: payments
Pod: payment-api-7d9f8c6f5b-x2k4m
Container: payment-api
User: root
Command: sh
Thời gian: 2026-10-09T10:15:32+07:00
Số lần lặp đã nén: 6

Chi tiết: <liên kết log hoặc sự kiện>
Dashboard: <liên kết Grafana đã gắn biến cluster namespace pod>
Runbook: <liên kết hướng dẫn xử lý rule>
```

Quy ước màu hoặc biểu tượng:

- `critical`: 🔴
- `warning`: 🟠
- `info`: 🔵
- `resolved`: 🟢

### 7.2 Biểu đồ và liên kết liên quan

Tin nhắn nên chứa deep link đến Grafana hoặc hệ thống log với biến `cluster`, `namespace`, `pod` và khoảng thời gian quanh sự kiện. Nếu hệ thống có Grafana Image Renderer, Sub Endpoint có thể đính kèm ảnh snapshot; nếu không, liên kết dashboard là phương án ổn định và ít tốn tài nguyên hơn.

Các liên kết phải được tạo từ allowlist domain. Không nối trực tiếp giá trị không kiểm soát vào URL để tránh chèn nội dung hoặc chuyển hướng ngoài ý muốn.

### 7.3 Quy tắc đa kênh

| Điều kiện | Telegram đội ứng dụng | Webhook đội ứng dụng | Kênh nền tảng hoặc SOC |
|---|:---:|:---:|:---:|
| `critical` | Có | Có | Có |
| `warning` | Có | Có | Tùy chính sách |
| `info` | Tùy chọn | Có thể gom batch | Không mặc định |
| Namespace chưa có owner | Không | Không | Có |
| `resolved` của critical | Có | Có | Có |

## 8. Cấu hình Falco và Falcosidekick tham khảo

### 8.1 Gửi Falco event qua HTTP

```yaml
json_output: true
json_include_output_property: true
http_output:
  enabled: true
  url: http://falcosidekick.falco.svc.cluster.local:2801/
```

Falco rule phải đưa các trường cần thiết vào output để chúng xuất hiện trong `output_fields`, tối thiểu gồm namespace và pod đối với workload Kubernetes.

### 8.2 Gửi sang Alertmanager

```yaml
alertmanager:
  hostport: http://alertmanager.monitoring.svc.cluster.local:9093
  endpoint: /api/v2/alerts
  expiresafter: 300
  minimumpriority: informational
  customseveritymap: >-
    emergency:critical,alert:critical,critical:critical,
    error:warning,warning:warning,notice:info,
    informational:info,debug:info
```

Falcosidekick hiện chuyển các key của `output_fields` thành label hợp lệ cho Alertmanager, ví dụ `k8s.ns.name` thành `k8s_ns_name`. Để có label tên chính xác là `namespace`, triển khai một bước chuẩn hóa trước Alertmanager hoặc sửa payload tại gateway ingest. Không nên dựa vào `extralabels` cho namespace vì cấu hình này phù hợp hơn với giá trị tĩnh.

## 9. Kế hoạch kiểm thử

### 9.1 Môi trường và dữ liệu kiểm thử

- Tạo namespace kiểm thử đại diện cho ít nhất hai đội trên DEV.
- Lặp lại bộ ca kiểm thử chính trên Staging.
- Dùng workload tạm thời, không chứa dữ liệu thật.
- Gắn `test_run_id` vào annotation hoặc log tương quan.
- Ghi thời gian tại bốn điểm: Falco phát hiện, Alertmanager nhận, Sub Endpoint nhận và kênh đích xác nhận.

### 9.2 Ma trận ca kiểm thử

| Mã | Kịch bản | Kết quả mong đợi |
|---|---|---|
| RT-01 | Alert từ namespace `payments` | Chỉ đến endpoint đội Payments và các route bổ sung được phép |
| RT-02 | Alert từ namespace `order` | Chỉ đến endpoint đội Order |
| RT-03 | Namespace chưa khai báo | Đến receiver mặc định của Platform |
| RT-04 | Critical tại namespace ứng dụng | Đến đội ứng dụng và kênh Platform hoặc SOC |
| SV-01 | Falco priority `Critical` | Severity sau chuẩn hóa là `critical` |
| SV-02 | Falco priority `Warning` | Severity sau chuẩn hóa là `warning` |
| SV-03 | Falco priority `Informational` | Severity sau chuẩn hóa là `info` |
| DD-01 | Gửi cùng payload 10 lần trong cửa sổ TTL | Chỉ một thông báo; bộ đếm duplicate tăng |
| DD-02 | Gửi cùng rule cho hai pod khác nhau | Tạo hai nhóm khi pod nằm trong khóa nhận diện |
| DD-03 | Gửi `resolved` sau `firing` | Thông báo resolved được chuyển tiếp |
| CH-01 | Telegram trả `429` | Retry theo `Retry-After`, không mất sự kiện |
| CH-02 | Webhook trả `500` | Retry và chuyển DLQ khi vượt ngưỡng |
| SEC-01 | Header xác thực sai | Trả `401` hoặc `403`, không xử lý payload |
| SEC-02 | Payload vượt giới hạn | Trả `413`, ghi metric lỗi, không ghi nội dung nhạy cảm |
| HA-01 | Một replica Sub Endpoint dừng | Replica còn lại tiếp tục nhận; không gửi trùng |

### 9.3 Cách tạo sự kiện Falco an toàn

Có thể triển khai một pod Alpine tạm trong namespace kiểm thử rồi mở shell tương tác để kích hoạt rule liên quan đến terminal shell trong container. Việc kiểm thử chỉ thực hiện tại DEV hoặc Staging, dùng tài khoản được cho phép và xóa workload sau khi thu thập đủ bằng chứng.

Ví dụ lệnh tham khảo:

```bash
kubectl -n payments-dev run falco-test --image=alpine --restart=Never -- sleep 3600
kubectl -n payments-dev exec -it falco-test -- sh
```

Tên rule và khả năng trigger phụ thuộc bộ luật Falco đang bật. Trước khi kiểm thử, cần xác nhận rule trong cấu hình thực tế và không dùng thao tác có thể thay đổi dữ liệu hoặc đặc quyền của cụm.

## 10. Chỉ tiêu nghiệm thu

| Chỉ tiêu | Mục tiêu đề xuất | Cách đo |
|---|---:|---|
| Tỷ lệ định tuyến đúng namespace | 100% trên bộ ca kiểm thử | So sánh receiver thực tế với ownership map |
| P95 từ Falco đến Sub Endpoint | ≤ 5 giây | Chênh lệch timestamp có cùng `test_run_id` |
| P95 từ Falco đến Telegram hoặc webhook | ≤ 10 giây | Timestamp Falco so với xác nhận kênh đích |
| Tỷ lệ gửi thành công sau retry | ≥ 99% trong cửa sổ kiểm thử | Metric success trên tổng request hợp lệ |
| Tỷ lệ lọc trùng ở bài DD-01 | ≥ 90% | `dedup_dropped_total / duplicate_input_total` |
| Cảnh báo bị mất | 0 | Đối soát event nhận với trạng thái gửi hoặc DLQ |
| Secret xuất hiện trong log | 0 | Quét log và kiểm tra thủ công |

### 10.1 Bảng ghi kết quả thực tế

| Môi trường | Thời gian chạy | Tổng event | Định tuyến đúng | P95 đến Sub Endpoint | P95 đến kênh đích | Bị lọc trùng | Lỗi cuối |
|---|---|---:|---:|---:|---:|---:|---:|
| DEV | Chưa cập nhật | - | - | - | - | - | - |
| Staging | Chưa cập nhật | - | - | - | - | - | - |

## 11. Giám sát vận hành

Sub Endpoint nên xuất các metric sau:

- `alert_gateway_requests_total{status,receiver}`
- `alert_gateway_alerts_total{severity,namespace,team}`
- `alert_gateway_dedup_dropped_total{severity,team}`
- `alert_gateway_delivery_total{channel,result,team}`
- `alert_gateway_delivery_duration_seconds{channel}`
- `alert_gateway_retry_total{channel,reason}`
- `alert_gateway_dlq_size`
- `alert_gateway_unknown_namespace_total`

Không nên gắn pod, command line hoặc event ID vào label metric vì gây cardinality cao. Những giá trị này chỉ nên xuất hiện trong structured log hoặc trace.

Dashboard vận hành cần thể hiện lưu lượng theo severity, độ trễ P50/P95/P99, tỷ lệ lỗi theo kênh, số cảnh báo bị lọc trùng, số namespace chưa có owner và kích thước DLQ. Cần có alert riêng khi Sub Endpoint không nhận sự kiện trong khoảng thời gian bất thường, vì trạng thái im lặng có thể là lỗi pipeline chứ không phải hệ thống an toàn.

## 12. Bảo mật và độ tin cậy

- Dùng TLS cho toàn bộ kết nối liên namespace; ưu tiên mTLS giữa Alertmanager và Sub Endpoint.
- Lưu Telegram bot token và webhook secret trong Secret Manager hoặc Kubernetes Secret được mã hóa, không ghi trực tiếp vào ConfigMap hoặc Git.
- Áp dụng NetworkPolicy chỉ cho phép Falco hoặc Falcosidekick gọi Alertmanager và Alertmanager gọi Sub Endpoint.
- Chạy container dưới non-root, filesystem chỉ đọc, bỏ Linux capabilities không cần thiết.
- Giới hạn request body, concurrency, timeout và rate limit theo nguồn.
- Làm sạch HTML hoặc Markdown trước khi gửi Telegram.
- Che command line, token, đường dẫn nhạy cảm theo chính sách dữ liệu.
- Dùng PodDisruptionBudget, anti-affinity và tối thiểu hai replica cho thành phần trung tâm.
- Sao lưu cấu hình, ownership map và template; kiểm thử khôi phục định kỳ.

## 13. Rủi ro và biện pháp giảm thiểu

| Rủi ro | Tác động | Biện pháp |
|---|---|---|
| Thiếu label namespace | Sai hoặc không định tuyến được | Receiver mặc định, metric unknown namespace, kiểm tra schema tại ingest |
| Label có cardinality cao | Alertmanager khó gom nhóm, tăng tài nguyên | Chỉ dùng label ổn định; chuyển dữ liệu động sang annotations |
| Namespace đổi owner nhưng config chưa cập nhật | Gửi sai đội | Ownership map qua GitOps, review bắt buộc, kiểm tra CI |
| Telegram hoặc webhook bị rate limit | Trễ hoặc mất thông báo | Queue, backoff, jitter, batch và DLQ |
| Nhiều replica gửi trùng | Nhiễu cảnh báo | Redis dùng chung và thao tác idempotent |
| Token lộ trong log hoặc Git | Mất an toàn kênh | Secret reference, redaction và quét secret |
| Route critical dừng ở nhánh đầu | SOC không nhận bản sao | Kiểm tra thứ tự route và `continue: true` |
| Rule Falco quá nhạy | Khối lượng cảnh báo cao | Tuning rule, exception có thời hạn và theo dõi tỷ lệ nhiễu |

## 14. Kế hoạch triển khai

### Giai đoạn 1 Chuẩn hóa và thử nghiệm DEV

- Kiểm kê namespace, owner và kênh nhận.
- Bật JSON output của Falco và xác nhận trường Kubernetes trong payload.
- Triển khai Falcosidekick hoặc gateway chuẩn hóa.
- Tạo Alertmanager route và receiver cho hai đội thí điểm.
- Triển khai Sub Endpoint, Redis và metric cơ bản.
- Chạy toàn bộ ca routing, severity và dedup tại DEV.

### Giai đoạn 2 Xác nhận Staging

- Đồng bộ cấu hình bằng GitOps.
- Kiểm thử HA, retry, rate limit, payload lỗi và mất kết nối kênh đích.
- Đo P50, P95, P99 và cập nhật bảng kết quả thực tế.
- Hoàn thiện runbook và quy trình thay đổi ownership map.

### Giai đoạn 3 Sẵn sàng sản xuất

- Review bảo mật và phân quyền secret.
- Chốt SLO, ngưỡng cảnh báo nội bộ và chính sách lưu DLQ.
- Triển khai canary theo nhóm namespace.
- Theo dõi nhiễu, sai tuyến và độ trễ trước khi mở rộng toàn bộ cụm.

## 15. Tài liệu vận hành cần bàn giao

1. Sơ đồ kiến trúc và luồng dữ liệu.
2. Danh sách label, annotation và quy tắc severity.
3. Alertmanager routing tree và ownership map.
4. Cấu hình triển khai Sub Endpoint, Redis, NetworkPolicy và secret reference.
5. Hướng dẫn thêm hoặc chuyển owner của namespace.
6. Runbook xử lý Telegram hoặc webhook lỗi, queue tăng, Redis lỗi và namespace không xác định.
7. Bộ ca kiểm thử tự động và cách tạo test event an toàn.
8. Dashboard cùng danh sách metric và alert nội bộ.
9. Biên bản kết quả DEV và Staging có số liệu độ trễ thực tế.

## 16. Kết luận

Giải pháp đề xuất đáp ứng nhu cầu phân tách cảnh báo Falco theo namespace trên các cụm Kubernetes tập trung, đồng thời giữ Alertmanager làm lớp định tuyến thống nhất và Sub Endpoint làm lớp tích hợp nghiệp vụ. Điểm quyết định chất lượng hệ thống là chuẩn hóa chính xác label `namespace`, kiểm soát cardinality, thực hiện chống trùng trên kho trạng thái dùng chung và luôn có receiver mặc định cho namespace chưa được ánh xạ.

Trước khi áp dụng cho Production, cần hoàn thành kiểm thử DEV và Staging, ghi nhận số liệu độ trễ thực tế, xác nhận không có cảnh báo sai tuyến, thử lỗi từng kênh đích và được phê duyệt về quản lý secret. Sau khi các tiêu chí nghiệm thu đạt yêu cầu, kiến trúc có thể mở rộng theo số lượng namespace mà không cần thay đổi thành phần lõi.

## Tài liệu tham khảo

1. Falco, Output Channels: https://falco.org/docs/concepts/outputs/channels/
2. Falco, Supported Fields for Conditions and Outputs: https://falco.org/docs/rules/supported-fields/
3. Falcosidekick, tài liệu dự án: https://github.com/falcosecurity/falcosidekick
4. Falcosidekick, Alertmanager output: https://github.com/falcosecurity/falcosidekick/blob/master/docs/outputs/alertmanager.md
5. Prometheus, Alertmanager Configuration: https://prometheus.io/docs/alerting/latest/configuration/
