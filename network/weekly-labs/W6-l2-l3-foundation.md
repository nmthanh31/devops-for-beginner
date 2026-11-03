# W6 Lab chính — Namespace, bridge và hai VLAN

Nếu cần lệnh và ý nghĩa từng tham số, xem [hướng dẫn dựng topology W6](./W6-guided-topology.md) sau khi tự dự đoán cách làm.

## Mục tiêu

Tự dựng topology cô lập, chứng minh traffic cùng VLAN đi được và khác VLAN không đi trực tiếp, giải thích bằng address plan + bridge table + pcap. Không gắn NIC quản trị của VM vào bridge lab.

```text
A1 (VLAN 10) ─┐             ┌─ A2 (VLAN 10)
              ├─ br-w6 ─────┤
B1 (VLAN 20) ─┘             └─ B2 (VLAN 20)
```

Mỗi endpoint là một network namespace nối vào bridge bằng veth pair. Chọn hai subnet không overlap, ví dụ `10.66.10.0/24` và `10.66.20.0/24`. Ghi IP, MAC, port bridge và VLAN membership trước khi cấu hình.

## Giai đoạn 1 — baseline cùng subnet

1. Tạo hai namespace `w6-a1`, `w6-a2`, hai veth pair và bridge `br-w6`. Kiểm tra tên chưa tồn tại trước khi tạo.
2. Gán IP cùng subnet cho hai endpoint, bật `lo`, veth và bridge port.
3. Dùng `ip -n NAME addr`, `ip -n NAME route`, `bridge link`, `bridge fdb show` và `tcpdump -eni br-w6 'arp or icmp'`.
4. Dự đoán rồi chạy ping. Chỉ ra ARP request, ARP reply và ICMP echo trong capture.

`ip netns add` tạo stack riêng; `ip link add ... type veth peer name ...` tạo dây ảo; `ip link set ... master br-w6` đưa endpoint vào switch ảo; `ip -n NAME` chạy lệnh `ip` trong namespace; `bridge fdb show` xem MAC được bridge học.

## Giai đoạn 2 — hai VLAN

1. Thêm `w6-b1`, `w6-b2` với veth pair riêng và subnet thứ hai.
2. Bật VLAN filtering trên bridge lab; gán access port của A1/A2 vào VLAN 10 và B1/B2 vào VLAN 20, với PVID/untagged phù hợp.
3. Kiểm `bridge vlan show`, `bridge fdb show`, `ip -d link show br-w6`.
4. Positive: A1↔A2 và B1↔B2 ping được.
5. Negative: A1 không ARP trực tiếp tới B1 dù tạm đặt cùng prefix để kiểm tra cô lập VLAN; sau đó trả về address plan hai subnet.

## Giai đoạn 3 — break/fix và evidence

Tạo từng fault trong lab: sai prefix, interface `DOWN`, VLAN membership lệch, duplicate IP trong cùng VLAN. Với mỗi fault viết hypothesis trước command; thu ít nhất hai lớp evidence; sửa tối thiểu; positive và negative test; khôi phục topology chuẩn.

Không dùng duplicate IP trên NIC thật/VMware network. Nếu capture không thấy packet, xác minh interface capture trước khi kết luận.

## Bài nộp và gate

Nộp sơ đồ, bảng address/VLAN, output `ip`/`bridge`, capture gắn timestamp, bảng 7 fault. Gate Calendar: xác định đúng ít nhất 6/7 và sửa ít nhất 5/7. Cleanup chỉ nhắm `w6-*` và `br-w6`, sau khi kiểm process còn trong namespace.

Nguồn: [Linux bridge](https://docs.kernel.org/networking/bridge.html), [ip-netns](https://man7.org/linux/man-pages/man8/ip-netns.8.html).
