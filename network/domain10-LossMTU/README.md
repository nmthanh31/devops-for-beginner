# N10 — Packet Loss & MTU

> **Câu hỏi domain này trả lời:** Kết nối "có" nhưng chậm hoặc treo — do RTT, jitter, mất gói, hay packet quá lớn cho đường đi?

**Mô hình cần nhớ một câu:** *Đo riêng ICMP / TCP / HTTP; ping nhỏ OK mà transfer lớn treo thì nghĩ tới Path MTU và ICMP bị chặn.*

## Lộ trình

| # | Bài | Thời lượng | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | [Latency, jitter, loss](./docs/01-loss-latency.md) | 40′ | Đo ba lớp, đọc retransmission, dùng netem |
| 2 | [MTU, MSS, PMTUD](./docs/02-mtu-pmtud.md) | 45′ | Path MTU, black hole, tính `ping -s` |
| 3 | [Ví dụ: ping OK, transfer treo](./docs/03-pmtu-walkthrough.md) | 15′ | Chứng minh PMTU black hole |
| 4 | [Lab: netem & MTU](./lab/01-netem-and-mtu.md) | 90′ | Tạo loss, dò ngưỡng MTU, tạo black hole |

## Đạt domain khi bạn có thể

- [ ] Tạo và định vị loss/latency bằng netem + capture.
- [ ] Tính ngưỡng `ping -M do -s` từ MTU.
- [ ] Đọc `tracepath`, phân biệt lỗi tại source và ICMP từ router.
- [ ] Viết report dùng `tcpdump/tracepath/mtr/ss` (yêu cầu competency N10).

## Liên kết

- Trước: [N09](../domain09-FirewallConntrackNAT/README.md) · Tiếp theo: [N11 OSPF & VPN](../domain11-OSPFVPN/README.md)

## Nguồn

[tc-netem(8)](https://man7.org/linux/man-pages/man8/tc-netem.8.html) · [RFC 1191](https://www.rfc-editor.org/rfc/rfc1191) · [RFC 8201](https://www.rfc-editor.org/rfc/rfc8201)
