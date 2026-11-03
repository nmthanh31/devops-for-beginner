# N12 — Cloud & Kubernetes Network Path

> **Câu hỏi domain này trả lời:** Những gì đã học trên Linux (namespace, bridge, route, NAT, firewall, LB) xuất hiện dưới tên gì trong Docker, Kubernetes và AWS — và debug một flow qua chúng thế nào?

**Mô hình cần nhớ một câu:** *Cùng cơ chế, tên khác, thêm lớp do provider quản lý; thu evidence theo từng hop và tách control plane object khỏi packet path.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [Map Linux → Docker → AWS](./docs/01-cloud-network-map.md) | 40′ | SG vs NACL, NAT GW, LB target health, Docker publish |
| 2 | [K8s Service path](./docs/02-k8s-service-path.md) | 45′ | selector/port/targetPort, EndpointSlice, NetworkPolicy, Ingress |
| 3 | [Ví dụ: Service không có endpoint](./docs/03-service-fault-walkthrough.md) | 15′ | Kiểm 4 bề mặt |
| 4 | [Lab: Service path evidence](./lab/01-service-path-evidence.md) | 75′ | Selector fault vs targetPort fault |

## Đạt domain khi bạn có thể

- [ ] Map một flow Linux → Docker → K8s → AWS trên một sơ đồ.
- [ ] Debug Service: selector, readiness, targetPort, policy.
- [ ] Giải thích stateful SG vs stateless NACL.
- [ ] Có evidence client / dataplane / server (yêu cầu competency N12).

## Liên kết

- Trước: [N11](../domain11-OSPFVPN/README.md) · Lab tuần: [W8 network operations gate](../weekly-labs/W8-network-operations-gate.md)
- Dùng tiếp: W9 Containers, W10–W12 AWS, W16 Argo CD.

## Nguồn

[Kubernetes Service](https://kubernetes.io/docs/concepts/services-networking/service/) · [EndpointSlice](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/) · [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/) · [AWS VPC security](https://docs.aws.amazon.com/vpc/latest/userguide/infrastructure-security.html)
