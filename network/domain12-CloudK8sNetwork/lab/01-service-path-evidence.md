# N12 Lab — Vẽ và chứng minh Service path

| | |
|---|---|
| **Thời lượng** | 75 phút |
| **Môi trường** | Cluster lab (kind / k3d / minikube) + `kubectl`. Namespace riêng `n12` |
| **Mục tiêu** | Chứng minh 3 bề mặt (control plane object, dataplane connection, app response); tạo và sửa lỗi selector + targetPort |
| **An toàn** | Không sửa Service phục vụ workload thật |

> Chưa có cluster: vẽ flow từ output mẫu trong docs Kubernetes, viết bảng câu hỏi/lệnh cho từng hop, và **ghi rõ đây là bài phân tích, chưa chạy**.

## Bước 0 — Workload lab

```bash
kubectl create namespace n12
kubectl -n n12 create deployment api --image=nginx:1.27 --replicas=2
kubectl -n n12 expose deployment api --port=80 --target-port=80
kubectl -n n12 run client --image=busybox:1.36 --restart=Never -- sleep 3600
kubectl -n n12 wait --for=condition=Ready pod --all --timeout=90s
```

## Bước 1 — Ghi lại Service path

```bash
kubectl -n n12 get svc api -o wide
kubectl -n n12 get pods -o wide --show-labels
kubectl -n n12 get endpointslices -l kubernetes.io/service-name=api -o yaml
```

| Mục | Giá trị |
|---|---|
| ClusterIP:port | |
| targetPort | |
| selector | |
| Pod IP:port trong EndpointSlice (ready?) | |

Vẽ: `client → DNS → ClusterIP:80 → dataplane → PodIP:80 → nginx`.

## Bước 2 — Ba bề mặt

```bash
kubectl -n n12 exec client -- nslookup api.n12.svc.cluster.local     # DNS
kubectl -n n12 exec client -- wget -qO- -T 3 http://api/ | head -3     # qua Service
POD_IP=$(kubectl -n n12 get pod -l app=api -o jsonpath='{.items[0].status.podIP}')
kubectl -n n12 exec client -- wget -qO- -T 3 http://$POD_IP/ | head -3 # thẳng pod
```

## Bước 3 — Fault 1: selector sai

**Dự đoán:** EndpointSlice và response sẽ ra sao?

```bash
kubectl -n n12 patch svc api -p '{"spec":{"selector":{"app":"api-v2"}}}'
kubectl -n n12 get endpointslices -l kubernetes.io/service-name=api -o jsonpath='{.items[*].endpoints}'; echo
kubectl -n n12 exec client -- wget -qO- -T 3 http://api/ ; echo "exit=$?"
kubectl -n n12 patch svc api -p '{"spec":{"selector":{"app":"api"}}}'     # sửa
```

## Bước 4 — Fault 2: targetPort sai

```bash
kubectl -n n12 patch svc api --type=json -p '[{"op":"replace","path":"/spec/ports/0/targetPort","value":8080}]'
kubectl -n n12 get endpointslices -l kubernetes.io/service-name=api -o yaml | grep -A3 ports
kubectl -n n12 exec client -- wget -qO- -T 3 http://api/ ; echo "exit=$?"
kubectl -n n12 patch svc api --type=json -p '[{"op":"replace","path":"/spec/ports/0/targetPort","value":80}]'
```

So sánh: fault 1 EndpointSlice **rỗng**; fault 2 EndpointSlice **có endpoint ready** (port 8080) nhưng connection bị **refused**. Giải thích vì sao khác.

## Bước 5 (tùy chọn) — NetworkPolicy

Áp một policy deny-all ingress cho `app=api`. Nếu CNI hỗ trợ, request fail; nếu không (ví dụ kind với kindnet cũ), request vẫn qua → ghi lại: object tồn tại ≠ được enforce.

---

## Definition of Done

- [ ] Bảng Service path + sơ đồ.
- [ ] Ba bề mặt: DNS, Service, Pod trực tiếp.
- [ ] Fault 1 và 2: dự đoán, evidence EndpointSlice + response, sửa, verify.
- [ ] Giải thích bằng lời: selector → EndpointSlice → targetPort → socket.

## Cleanup

```bash
kubectl delete namespace n12
```
