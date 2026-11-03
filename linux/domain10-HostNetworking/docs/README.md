# L10 — Host Networking · Theory

## Phạm vi và nguồn

Phần cốt lõi đối chiếu [LPIC-1 Objectives V5.0 — Topic 109](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0):

- **109.1:** network mask, CIDR, TCP, UDP, ICMP, IPv4, IPv6 và các port phổ biến.
- **109.2:** persistent network configuration, NetworkManager và nhận thức về systemd-networkd.
- **109.3:** `iproute2`, route, `ss`, `ping`, `traceroute`, `tracepath`, `netcat` và troubleshooting.
- **109.4:** `/etc/hosts`, `/etc/resolv.conf`, `/etc/nsswitch.conf`, `dig`, `host`, `getent` và systemd-resolved.

L10 tập trung vào network của **một Linux host**. Firewall và SSH hardening được học sâu ở L11; routing giữa nhiều mạng, bridge, NAT và network namespace được học trong Network domain.

## Thứ tự học

1. [Luồng packet trên Linux host](./01-host-network-flow.md)
2. [Interface, địa chỉ IP và CIDR](./02-interfaces-addresses-cidr.md)
3. [Route, gateway và neighbor](./03-routing-gateway-neighbor.md)
4. [TCP, UDP, socket và port](./04-transport-sockets-ports.md)
5. [Hostname và DNS client](./05-hostname-and-dns.md)
6. [Cấu hình mạng bền vững](./06-persistent-network-configuration.md)
7. [Quy trình troubleshooting theo lớp](./07-network-troubleshooting.md)
8. [Command reference](./00-command-reference.md)

## Mô hình tư duy

```text
tên miền
   ↓ DNS
địa chỉ đích
   ↓ route lookup
interface + next hop
   ↓ neighbor/link
packet rời host
   ↓
remote IP:port
   ↓
process đang listen
```

Mỗi bước có một bề mặt quan sát khác nhau. `ping`, `dig`, `ip route` và `ss` không trả lời cùng một câu hỏi.

## Cách học từng thành phần

Với mỗi khái niệm, luôn trả lời đủ ba câu:

1. **Là gì?** Thành phần thuộc user space, kernel, local host hay thiết bị mạng?
2. **Để làm gì?** Nó giải quyết vấn đề nào trong quá trình giao tiếp?
3. **Hoạt động thế nào?** Input của nó là gì, nó đưa ra quyết định gì và output chuyển tới đâu?

Sau đó mới học lệnh quan sát. Lệnh là cách nhìn vào cơ chế, không phải bản thân cơ chế.

Mỗi khái niệm có một bài chịu trách nhiệm giải thích chính. Khi bài sau cần dùng lại khái niệm cũ, tài liệu sẽ nhắc ngắn và dẫn về bài trước thay vì chép lại toàn bộ định nghĩa.
