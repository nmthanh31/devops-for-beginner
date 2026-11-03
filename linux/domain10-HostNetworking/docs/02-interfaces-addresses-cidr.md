# Bài 2 — Interface, địa chỉ IP và CIDR

## Mục tiêu và tiền đề

Bài 1 đã giải thích luồng tổng quát, NIC, driver và interface. Bài này đi sâu vào trạng thái của interface và cách IP/prefix xác định local subnet.

Đọc trước: [Luồng packet trên Linux host](./01-host-network-flow.md).

## 1. Interface hoạt động như thế nào?

Interface là đối tượng kernel dùng để gửi và nhận traffic. Nó có:

- tên như `ens33`;
- trạng thái administrative và operational;
- MAC address;
- MTU;
- một hoặc nhiều IPv4/IPv6 address;
- hàng đợi packet.

Linux còn có interface không gắn trực tiếp với NIC, ví dụ:

- `lo`: loopback;
- bridge;
- VLAN;
- tunnel;
- veth của container/network namespace.

### `UP` và `LOWER_UP`

- `UP`: interface được bật về mặt quản trị.
- `LOWER_UP`: lớp phía dưới báo có carrier/link.

Interface có `UP` nhưng thiếu `LOWER_UP` có thể đã được bật nhưng virtual cable/card/link chưa kết nối.

```bash
ip -br link
ip link show dev ens33
```

## 2. MAC, frame và local link

MAC address dùng để giao Ethernet frame trong cùng local Layer-2 network. Switch học source MAC và chuyển frame theo destination MAC.

MAC không thay thế IP:

- MAC phục vụ link hiện tại;
- IP cho phép packet đi qua nhiều network/router.

```bash
ip link show dev ens33
```

Trường `link/ether` hiển thị MAC của interface.

## 3. IPv4, IPv6 và loopback

### IPv4

IPv4 dài 32 bit, thường viết dạng dotted decimal như `192.168.220.133`.

### IPv6

IPv6 dài 128 bit, viết dạng hexadecimal như `2001:db8::10`. Một interface có thể đồng thời giữ nhiều IPv6 address với scope/lifetime khác nhau.

Một số địa chỉ đặc biệt:

- `127.0.0.1`: IPv4 loopback;
- `::1`: IPv6 loopback;
- `fe80::/10`: IPv6 link-local.

### Loopback

`lo` là interface để host giao tiếp với chính nó. Traffic loopback không đi ra NIC.

Service bind `127.0.0.1` chỉ nhận traffic local. Máy Windows không thể truy cập loopback bên trong VM.

## 4. Prefix, CIDR, netmask và subnet

### Prefix và CIDR

Prefix cho biết bao nhiêu bit đầu của IP thuộc phần network. CIDR viết address cùng prefix:

```text
192.168.220.133/24
```

IPv4 có 32 bit. `/24` nghĩa 24 bit đầu là network, 8 bit còn lại thuộc phần host trong block.

### Netmask

Netmask là cách IPv4 truyền thống biểu diễn phần network bằng bit `1`:

```text
/24 = 255.255.255.0
```

### Subnet

Subnet là dải địa chỉ cùng network prefix. Nếu destination nằm trong connected subnet, host thường gửi trực tiếp tới destination neighbor thay vì gateway.

Với `192.168.220.133/24`:

```text
network address:   192.168.220.0
host address:      192.168.220.133
broadcast address: 192.168.220.255
```

Trong subnet IPv4 truyền thống này, host address thường nằm từ `.1` đến `.254`.

| CIDR | Netmask | Tổng số địa chỉ trong block |
|---|---|---:|
| `/8` | `255.0.0.0` | 16,777,216 |
| `/16` | `255.255.0.0` | 65,536 |
| `/24` | `255.255.255.0` | 256 |
| `/32` | `255.255.255.255` | 1 |

## 5. Source và destination address

Mỗi IP packet có source IP và destination IP.

Một interface có thể giữ nhiều IP. Nếu process không bind source IP cụ thể, kernel dựa vào route, interface đầu ra, scope và rule chọn địa chỉ để chọn source IP.

```bash
ip route get 8.8.8.8
```

Output thường cho biết `src` mà kernel dự kiến dùng.

## 6. Address scope và lifetime

`ip addr` có thể hiển thị:

- `scope host`: chỉ trong host;
- `scope link`: chỉ local link;
- `scope global`: phạm vi rộng hơn link;
- `dynamic`: được cấp động;
- `valid_lft`, `preferred_lft`: lifetime của address.

`scope global` không tự động có nghĩa địa chỉ public Internet.

```bash
ip -br addr
ip addr show dev ens33
```

## 7. Static address, dynamic address và DHCP

- **Static address:** admin khai báo address/prefix cố định.
- **Dynamic address:** được cấp bởi DHCP hoặc cơ chế tự động và thường có lease/lifetime.

DHCP có thể cấp IP, prefix/netmask, default gateway, DNS và search domain. Dynamic không nhất thiết thay đổi liên tục, nhưng client không nên coi IP là vĩnh viễn nếu không có reservation/design phù hợp.

## 8. MTU

MTU là kích thước IP packet tối đa interface định truyền mà không phải xử lý packet quá lớn theo cơ chế liên quan.

Ethernet thường gặp MTU 1500. Tunnel, VPN hoặc overlay thêm header nên có thể cần MTU nhỏ hơn.

MTU/path MTU lỗi có thể tạo triệu chứng:

```text
ping nhỏ thành công
nhưng request lớn treo hoặc timeout
```

```bash
ip link show dev ens33
tracepath DESTINATION
```

## 9. Runtime address không persistent

```bash
sudo ip addr add 192.0.2.10/24 dev ens33
```

Lệnh này thay đổi runtime kernel. Address có thể mất sau reboot hoặc khi network manager cấu hình lại. Persistent configuration được học ở Bài 6.

<!-- learn:tail -->
## Tự kiểm tra

1. `ip -br link` thấy `ens33 UP` nhưng `ip link` không có `LOWER_UP`. Nghĩa gì?
2. IP thêm bằng `ip addr add` mất sau reboot. Vì sao?

<details>
<summary>Đáp án</summary>

1. Admin đã bật interface nhưng không có carrier (cáp/vNIC chưa nối).
2. Đó là cấu hình runtime; cần cấu hình persistent (Netplan/NetworkManager — Bài 6).

</details>

## Nguồn

- [LPIC-1 V5.0 — Objectives 109.1 và 109.3](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

