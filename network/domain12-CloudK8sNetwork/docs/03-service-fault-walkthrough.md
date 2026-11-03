# N12 Ví dụ — Service tồn tại nhưng không có endpoint

## Bối cảnh

Service `api` (ns `lab`): ClusterIP `10.96.4.20`, `port 80`, `targetPort 8080`, `selector app=api`. DNS trả `10.96.4.20`. Client resolve được, HTTP fail.

> ✋ Liệt kê 4 bề mặt cần kiểm theo thứ tự trước khi đọc tiếp.

## Điều tra

```bash
kubectl get svc api -n lab -o yaml
kubectl get pods -n lab -l app=api --show-labels -o wide            # → No resources found
kubectl get pods -n lab --show-labels                               # → app=api-v2
kubectl get endpointslices -n lab -l kubernetes.io/service-name=api -o yaml   # endpoints: null
kubectl get networkpolicy -n lab
```

| Bề mặt | Kết quả |
|---|---|
| DNS | ✅ `10.96.4.20` |
| Service object | ✅ tồn tại |
| EndpointSlice | ❌ rỗng — selector `app=api` không khớp pod `app=api-v2` |

**Fix:** sửa selector của Service **lab** hoặc label pod theo thiết kế (không sửa Service đang phục vụ workload thật). Verify: EndpointSlice có endpoint `ready: true` → curl từ client pod.

## Nếu EndpointSlice có pod mà vẫn fail

1. `targetPort` khớp port app nghe? (`kubectl exec POD -- ss -lntp`)
2. Pod readiness đúng?
3. NetworkPolicy / CNI có chặn?
4. Dataplane có lập trình rule? (cách xem phụ thuộc kube-proxy mode hoặc CNI)

## Bài học

```text
DNS PASS ≠ Service object PASS ≠ EndpointSlice PASS ≠ packet tới pod
```

Ghi riêng từng bằng chứng để không nhầm lỗi control plane với lỗi packet path.
