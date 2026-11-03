# N12 Bài 1 — Ánh xạ cơ chế Linux sang Docker và cloud

> **Sau bài này bạn sẽ:**
> - Map mỗi khái niệm N01–N11 sang tên gọi trên Docker và AWS.
> - Biết thêm các **lớp điều khiển của provider** nằm trước host.
> - Thu evidence theo từng hop của một flow cloud.
>
> **Cần trước:** N01–N11. Sẽ dùng lại ở W10–W12 (AWS manual).

---

## 1. Ý tưởng chính

Cloud và container **dùng lại** những cơ chế bạn đã học — chỉ đổi tên và thêm lớp do provider quản lý. Cùng triệu chứng "timeout" có thể nằm ở bất kỳ lớp nào; phải ghi đường đi thực tế và nơi có telemetry.

## 2. Bảng ánh xạ

| Đã học (Linux) | Docker | AWS | Câu hỏi vận hành |
|---|---|---|---|
| Network namespace (N04) | Network namespace của container | (ENI trên instance) | Đang nhìn stack nào? |
| veth + bridge (N04) | `docker0` / user bridge + veth | — | Container nối vào đâu? |
| IP/prefix/subnet (N03) | Subnet của Docker network | **VPC / subnet** | Đúng dải? Overlap với VPN/on-prem? |
| Route table (N05) | Route trong container (default → bridge) | **Subnet route table** | Next hop là local / IGW / NAT GW / TGW? |
| Stateful firewall (N09) | iptables/nft do Docker quản lý | **Security group** (stateful) | Inbound/outbound cho flow? |
| Stateless filter | — | **Network ACL** (stateless) | Có chặn **chiều về** (ephemeral ports)? |
| SNAT/masquerade (N09) | Container đi ra ngoài | **NAT gateway** | Private host đi ra & về thế nào? |
| DNAT / port forward (N09) | `-p 8080:80` | LB listener → target | Port host ↔ port container/target? |
| Reverse proxy/LB + health (N08) | — | **ALB/NLB** + target health | Listener, rule, target, health path? |
| DNS (N06) | DNS nhúng `127.0.0.11` | Route 53 / VPC resolver | Tên trả đúng IP? |

> Đây là **ánh xạ khái niệm**, không phải "cloud chạy y hệt kernel Linux". Semantics cụ thể thuộc về provider.

### AWS: Security group vs Network ACL

| | Security group | Network ACL |
|---|---|---|
| Gắn vào | ENI (instance) | Subnet |
| State | **Stateful** — reply tự cho qua | **Stateless** — phải mở cả chiều về |
| Rule | Chỉ allow | Allow + deny, xét theo số thứ tự |

Target LB `unhealthy` có thể do listener/health path/port/SG sai — dù instance ping và SSH được.

---

## 3. Một flow cloud và evidence từng hop

```text
client → DNS → public ALB (listener/rule) → healthy target
       → subnet route/NACL → SG → instance ENI
       → host firewall → app socket → app log
```

| Hop | Evidence |
|---|---|
| DNS | `dig` answer |
| LB | Listener/rule, **target health reason** |
| Subnet | Route table, NACL |
| Instance | SG, `ss -lntp`, host firewall |
| App | Access/error log |

> **Đừng sửa LB và instance firewall cùng lúc** — một thay đổi mỗi lần.

## 4. Docker cũng là N04 + N09

```text
container ns ─ eth0 ═ veth ═ docker0 (bridge) ─ host ─ NAT (masquerade ra, DNAT cho -p)
```

`docker ps` thấy container `Up` **không** chứng minh app bind đúng interface trong container hay port đã publish. Chuỗi kiểm:

1. Listener trong container: `docker exec C ss -lntp` (app bind `127.0.0.1` trong container → không publish được).
2. Container IP/route: `docker inspect`.
3. Port publish/NAT: `docker port C`, `nft list ruleset`.
4. Host listener: `ss -lntp | grep 8080`.
5. Client path.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "SG mở inbound là đủ." | NACL stateless cần mở chiều về. |
| "Instance SSH được thì LB health phải OK." | Health dùng port/path khác. |
| "Container Up = service truy cập được." | Còn bind, publish, NAT. |

## Tự kiểm tra

1. Mở SG inbound 443, NACL inbound 443 allow, NACL outbound chỉ allow 443. Client HTTPS có chạy không?
2. App trong container bind `127.0.0.1:80`, chạy `-p 8080:80`. `curl host:8080` ra gì?

<details>
<summary>Đáp án</summary>

1. Không — reply đi ra tới ephemeral port của client (1024–65535), NACL outbound chặn.
2. Lỗi (thường `Connection reset`/empty reply) — DNAT tới IP container, nhưng app chỉ nghe loopback của container.

</details>

## Nguồn

[AWS VPC security](https://docs.aws.amazon.com/vpc/latest/userguide/infrastructure-security.html) · [Docker bridge](https://docs.docker.com/engine/network/drivers/bridge/) · [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/)
