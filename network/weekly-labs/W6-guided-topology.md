# W6 Hướng dẫn thực hành — Dựng hai VLAN từ một VM

Đọc [N01](../domain01-EncapsulationEthernet/README.md) → [N04](../domain04-NetnsVethBridgeVLAN/README.md) trước. Mục tiêu là nhìn thấy **vì sao** A1 nói được với A2, B1 nói được với B2, còn A1 không tự ARP tới B1 qua VLAN khác.

Chạy trên VM lab có `iproute2`, `bridge` và `tcpdump`; các lệnh dưới đây cần `sudo`. Không nối NIC quản trị/SSH vào `br-w6`. Mọi tên `w6-*` và `br-w6` phải chưa tồn tại; kiểm `ip netns list` và `ip -br link` trước. Nếu chúng đã tồn tại, dừng để xem tài nguyên đó là gì, không xóa bừa.

## 1. Tạo switch ảo và hai máy A

```bash
sudo ip link add br-w6 type bridge
sudo ip link set br-w6 up
sudo ip netns add w6-a1
sudo ip netns add w6-a2
sudo ip link add w6-a1-h type veth peer name w6-a1-n
sudo ip link add w6-a2-h type veth peer name w6-a2-n
sudo ip link set w6-a1-n netns w6-a1
sudo ip link set w6-a2-n netns w6-a2
sudo ip link set w6-a1-h master br-w6
sudo ip link set w6-a2-h master br-w6
sudo ip link set w6-a1-h up
sudo ip link set w6-a2-h up
```

`ip link add br-w6 type bridge` tạo bridge Layer 2; `up` bật nó. `ip netns add` tạo network stack riêng cho A1/A2. `type veth peer name` tạo hai đầu dây ảo; đuôi `-h` ở host, đuôi `-n` được chuyển vào namespace bằng `netns`. `master br-w6` gắn đầu host thành port của bridge; port phải `up` mới chuyển frame.

Gán IP ở **đầu trong namespace**; bridge port ở host không cần IP cho bài Layer 2 này:

```bash
sudo ip -n w6-a1 addr add 10.66.10.11/24 dev w6-a1-n
sudo ip -n w6-a2 addr add 10.66.10.12/24 dev w6-a2-n
sudo ip -n w6-a1 link set lo up
sudo ip -n w6-a2 link set lo up
sudo ip -n w6-a1 link set w6-a1-n up
sudo ip -n w6-a2 link set w6-a2-n up
sudo ip -n w6-a1 route get 10.66.10.12
sudo ip netns exec w6-a1 ping -c 2 10.66.10.12
```

`-n w6-a1` yêu cầu lệnh `ip` chạy trong namespace A1; `addr add` gắn địa chỉ/prefix lên interface; `dev` chỉ interface. `route get` dự đoán egress và source IP. `ip netns exec` chạy chương trình `ping` trong namespace A1; `-c 2` dừng sau hai Echo Request. Không có gateway ở đây: hai IP cùng `/24` nên route connected cho phép A1 ARP trực tiếp A2.

Trước khi ping, mở terminal khác để capture:

```bash
sudo tcpdump -eni br-w6 'arp or icmp'
```

`-e` hiện Ethernet header/MAC, `-n` giữ địa chỉ số, `-i br-w6` chọn bridge, biểu thức lọc chỉ ARP hoặc ICMP. Dự đoán ARP request, ARP reply và ICMP Echo/Reply; nếu không thấy, thử capture trên `w6-a1-h` và kiểm bridge port/capture point. Xem thêm `ip -n w6-a1 neigh` (IP→MAC) và `bridge fdb show br br-w6` (MAC→port); hai bảng có mục đích khác nhau.

## 2. Thêm hai máy B

```bash
sudo ip netns add w6-b1
sudo ip netns add w6-b2
sudo ip link add w6-b1-h type veth peer name w6-b1-n
sudo ip link add w6-b2-h type veth peer name w6-b2-n
sudo ip link set w6-b1-n netns w6-b1
sudo ip link set w6-b2-n netns w6-b2
sudo ip link set w6-b1-h master br-w6
sudo ip link set w6-b2-h master br-w6
sudo ip link set w6-b1-h up
sudo ip link set w6-b2-h up
sudo ip -n w6-b1 addr add 10.66.20.11/24 dev w6-b1-n
sudo ip -n w6-b2 addr add 10.66.20.12/24 dev w6-b2-n
sudo ip -n w6-b1 link set lo up
sudo ip -n w6-b2 link set lo up
sudo ip -n w6-b1 link set w6-b1-n up
sudo ip -n w6-b2 link set w6-b2-n up
```

B1/B2 cùng subnet `10.66.20.0/24`. Lúc này bridge chưa bật VLAN filtering: A và B vẫn cùng broadcast domain Layer 2 dù chúng ở hai IPv4 subnet. Không ping được A1→B1 trong cấu hình hiện tại **chưa chứng minh** VLAN isolation: không có route/gateway giữa hai subnet. Bước sau mới kiểm đúng thuộc tính VLAN.

## 3. Chia bridge thành VLAN 10 và VLAN 20

```bash
sudo ip link set dev br-w6 type bridge vlan_filtering 1
sudo bridge vlan del dev w6-a1-h vid 1
sudo bridge vlan del dev w6-a2-h vid 1
sudo bridge vlan del dev w6-b1-h vid 1
sudo bridge vlan del dev w6-b2-h vid 1
sudo bridge vlan add dev w6-a1-h vid 10 pvid untagged
sudo bridge vlan add dev w6-a2-h vid 10 pvid untagged
sudo bridge vlan add dev w6-b1-h vid 20 pvid untagged
sudo bridge vlan add dev w6-b2-h vid 20 pvid untagged
bridge vlan show
```

`vlan_filtering 1` bật kiểm VLAN của bridge. Một port bridge mới có thể mang VLAN 1 mặc định; `del ... vid 1` bỏ membership đó để test không bị đường vòng ngoài ý muốn. `vid 10` chọn VLAN 10; `pvid` gán frame **không tag đi vào** cho VLAN này; `untagged` gửi frame ra endpoint **không tag**. Bốn namespace không cần biết tag, vì các port của chúng là access port.

Kiểm positive:

```bash
sudo ip netns exec w6-a1 ping -c 2 10.66.10.12
sudo ip netns exec w6-b1 ping -c 2 10.66.20.12
bridge vlan show
```

Để kiểm negative VLAN thật sự, tạm cho A1 một địa chỉ **cùng prefix với B1** nhưng khác IP, rồi hỏi B1. Nếu chỉ test A1 `.10/24` tới B1 `.20/24`, kernel sẽ báo không có route trước khi tạo ARP; ta chưa kiểm được VLAN.

```bash
sudo ip -n w6-a1 addr add 10.66.20.99/24 dev w6-a1-n
sudo ip -n w6-a1 route get 10.66.20.11 from 10.66.20.99
sudo ip netns exec w6-a1 ping -I 10.66.20.99 -c 2 -W 1 10.66.20.11
sudo ip -n w6-a1 neigh show 10.66.20.11
sudo ip -n w6-a1 addr del 10.66.20.99/24 dev w6-a1-n
```

`ping -I` chọn source IP vừa thêm, `-W 1` giới hạn chờ reply; `neigh show` giúp thấy ARP không hoàn tất nếu request không vượt VLAN. Address tạm chỉ tồn tại trong namespace A1 và được xóa ngay sau test. Capture ở `w6-a1-h` và `w6-b1-h` cùng lúc: ARP request có thể thấy phía A1 nhưng không tới phía B1. Nếu B1 vẫn trả lời, kiểm `bridge vlan show`: port membership/PVID có thể sai.

## 4. Chẩn đoán và cleanup

Với một fault như `w6-a2-h down` hoặc sai VLAN ID, ghi dự đoán trước; lấy `ip -br link`, `bridge vlan show`, `ip neigh` và hai capture; sửa đúng một cấu hình rồi ping lại. Phân biệt rõ: route lookup quyết định **có cố gửi không**, ARP/ND quyết định **MAC next hop**, bridge/VLAN quyết định **frame đi qua port nào**.

Trước cleanup, kiểm process còn giữ namespace:

```bash
ip netns list
sudo ip netns pids w6-a1
sudo ip netns pids w6-a2
sudo ip netns pids w6-b1
sudo ip netns pids w6-b2
```

Sau khi đã dừng đúng process lab và xác nhận tên tài nguyên, xóa bốn namespace rồi bridge; các veth gắn với namespace sẽ biến mất cùng namespace. Kiểm lại `ip netns list`, `ip -br link` và `findmnt`/SSH nếu bạn đã thay đổi gì khác. Không dùng wildcard để xóa interface.

```bash
sudo ip netns del w6-a1
sudo ip netns del w6-a2
sudo ip netns del w6-b1
sudo ip netns del w6-b2
sudo ip link del br-w6
ip netns list
ip -br link
```

`ip netns del NAME` xóa named namespace; chỉ chạy sau khi `ip netns pids NAME` không còn process lab. `ip link del br-w6` xóa đúng bridge của bài này. Hai lệnh cuối là phép kiểm cleanup: không còn `w6-*` hoặc `br-w6` do bài lab tạo.

Nguồn: [ip-netns](https://man7.org/linux/man-pages/man8/ip-netns.8.html), [ip-link](https://man7.org/linux/man-pages/man8/ip-link.8.html), [Linux bridge](https://docs.kernel.org/networking/bridge.html).
