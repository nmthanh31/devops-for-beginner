# L10 — Host Networking

> **Câu hỏi domain này trả lời:** Một Linux host nhận IP, chọn route, phân giải tên và đưa traffic tới đúng socket của process như thế nào — và lỗi kết nối nằm ở lớp nào?

**Mô hình cần nhớ một câu:** *Tên → IP (DNS) → route (interface, next hop, src) → neighbor → packet → remote IP:port → listener → process; mỗi lớp có một lệnh quan sát riêng.*

```text
program → socket (IP+port) → TCP/UDP/ICMP → routing → interface → gateway → remote host
```

## Lộ trình

| # | Bài | Thời lượng | Câu hỏi chính |
|---|---|---|---|
| 1 | [Luồng packet trên host](./docs/01-host-network-flow.md) | 45′ | Outbound/inbound đi qua những gì? |
| 2 | [Interface, IP, CIDR](./docs/02-interfaces-addresses-cidr.md) | 40′ | `UP`/`LOWER_UP`, prefix, MTU |
| 3 | [Route, gateway, neighbor](./docs/03-routing-gateway-neighbor.md) | 40′ | Longest prefix, src IP, ARP |
| 4 | [TCP/UDP, socket, port](./docs/04-transport-sockets-ports.md) | 40′ | Bind address, TCP state |
| 5 | [Hostname & DNS client](./docs/05-hostname-and-dns.md) | 40′ | NSS, resolved, getent vs dig |
| 6 | [Cấu hình bền vững](./docs/06-persistent-network-configuration.md) | 40′ | Netplan, `netplan try` |
| 7 | [Troubleshooting theo lớp](./docs/07-network-troubleshooting.md) | 45′ | 9 bước gần → xa |
| — | [Lệnh cần nhớ](./docs/00-command-reference.md) · [Phạm vi LPIC](./docs/README.md) | — | — |
| Lab | [Windows → VM evidence](./lab/01-host-network-evidence.md) | 75′ | — |

## Đạt domain khi bạn có thể

- [ ] Chứng minh chuỗi process → listener → route → DNS → TCP bằng `ss`/`ip`/`resolvectl`/`curl`.
- [ ] Tái hiện và phân biệt refused / timeout / 404 có capture.
- [ ] Đổi cấu hình Netplan an toàn bằng `netplan try` (trên interface không phải SSH).
- [ ] Giải thích bind `127.0.0.1` vs `0.0.0.0` bằng test thật.

## Liên kết

- Trước: [L09](../domain9-ResourceTroubleshooting/README.md) · Tiếp theo: [L11 SSH & Host Security](../domain11-SSHHostSecurity/README.md)
- Đào sâu: [Network N01–N12](../../network/README.md)

## Nguồn

[LPIC-1 Topic 109](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0) · [Ubuntu Server networking](https://ubuntu.com/server/docs/explanation/networking/configuring-networks/)
