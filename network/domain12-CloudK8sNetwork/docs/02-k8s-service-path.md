# N12 Bài 2 — Pod, Service, EndpointSlice, NetworkPolicy, Ingress

> **Sau bài này bạn sẽ:**
> - Theo một request: DNS → ClusterIP → dataplane → EndpointSlice → Pod IP:targetPort → socket.
> - Phân biệt `port`, `targetPort`, `selector` — ba khâu hỏng độc lập.
> - Biết NetworkPolicy chỉ có hiệu lực khi CNI hỗ trợ.
>
> **Cần trước:** [Bài 1](./01-cloud-network-map.md).

---

## 1. Các thành phần

| Thành phần | Là gì | Tương ứng đã học |
|---|---|---|
| **Pod IP** | Địa chỉ pod trên pod network (do **CNI** cấp) | Namespace + veth (N04) |
| **Service / ClusterIP** | IP ảo ổn định cho một nhóm pod | DNAT + LB (N08, N09) |
| **EndpointSlice** | Danh sách pod IP:port đang backing Service + readiness | Backend pool + health |
| **Service proxy / dataplane** | kube-proxy (iptables/IPVS/nft) **hoặc** dataplane của CNI (eBPF...) | Firewall/NAT rule |
| **NetworkPolicy** | Quy định pod nào nói với pod nào | Firewall (N09) |
| **Ingress / Gateway API** | HTTP/TLS routing ở rìa cluster | Reverse proxy (N08) |

## 2. Đường đi một request

```text
client pod
  → DNS: api.lab.svc.cluster.local → 10.96.4.20 (ClusterIP)
  → dataplane DNAT: 10.96.4.20:80 → chọn 1 endpoint ready
  → EndpointSlice: 10.244.1.7:8080
  → Pod IP:targetPort → app socket
```

## 3. Ba khâu của Service

```yaml
apiVersion: v1
kind: Service
metadata: { name: api, namespace: lab }
spec:
  selector: { app: api }       # ① chọn pod theo label
  ports:
  - port: 80                   # ② cổng client gọi (ClusterIP:80)
    targetPort: 8080           # ③ cổng app trong pod nghe
```

| Khâu sai | Triệu chứng | Evidence |
|---|---|---|
| ① selector không khớp label | EndpointSlice **rỗng** | `get pods --show-labels` vs selector |
| Pod chưa ready | Endpoint có nhưng `ready: false` | EndpointSlice `conditions` |
| ③ targetPort ≠ port app nghe | Endpoint ready nhưng refused | `kubectl exec ... ss -lntp` |

> DNS PASS + Service object tồn tại **không** chứng minh có backend.

## 4. Lệnh

```bash
kubectl get svc -n NS
kubectl get endpointslices -n NS -l kubernetes.io/service-name=NAME -o yaml   # xem conditions + ports
kubectl get pods -n NS -o wide --show-labels
kubectl get networkpolicy -n NS
```

- Ưu tiên **EndpointSlice**; `kubectl get endpoints` là API cũ.
- Không mặc định mọi cluster dùng iptables — dataplane tùy kube-proxy mode hoặc CNI.

## 5. NetworkPolicy

Mô tả traffic được phép giữa pod/namespace. **Enforcement cần CNI hỗ trợ** (Calico, Cilium...). Có object NetworkPolicy không chứng minh nó đang được thực thi — test positive/negative từ pod thật.

## 6. Ingress — thêm một tầng, không thay Service

```text
client → DNS/cert → Ingress controller (rule host/path) → Service → EndpointSlice → Pod
```

Evidence từng cạnh: DNS/cert/Ingress rule → Service selector/port → EndpointSlice readiness/port → Pod IP/listener → NetworkPolicy.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Ping ClusterIP để test Service." | ClusterIP là IP ảo cho port cụ thể; ICMP thường không trả lời. |
| "Sửa selector xong vẫn lỗi → lỗi DNS." | Kiểm targetPort và bind của app trước. |
| "Có NetworkPolicy là an toàn." | Cần CNI enforce. |

## Tự kiểm tra

1. EndpointSlice có 2 endpoint `ready: true`, curl Service báo refused. Nghi gì?
2. Selector `app=api`, pod label `app=api-v2`. EndpointSlice thế nào?

<details>
<summary>Đáp án</summary>

1. `targetPort` không khớp port app nghe (hoặc app bind `127.0.0.1` trong pod).
2. Không có endpoint nào.

</details>

## Nguồn

[Service](https://kubernetes.io/docs/concepts/services-networking/service/) · [EndpointSlice](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/) · [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
