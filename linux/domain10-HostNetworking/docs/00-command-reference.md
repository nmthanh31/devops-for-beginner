# L10 — Command reference

## Interface và address

```bash
ip -br link
ip -br addr
ip link show dev INTERFACE
ip addr show dev INTERFACE
hostname -I
```

| Argument | Ý nghĩa |
|---|---|
| `-br` | Brief output |
| `link` | Thông tin lớp link/interface |
| `addr` | Địa chỉ gắn trên interface |
| `show dev ens33` | Chỉ xem device đã chọn |
| `hostname -I` | Liệt kê các địa chỉ của host; không phải chỉ một địa chỉ duy nhất |

Các trường cần đọc trong `ip link`:

| Trường | Ý nghĩa |
|---|---|
| `UP` | Interface được bật về mặt quản trị |
| `LOWER_UP` | Lớp dưới/carrier đang hoạt động |
| `mtu` | Maximum Transmission Unit |
| `link/ether` | MAC address |
| `state` | Operational state |

Các trường cần đọc trong `ip addr`:

| Trường | Ý nghĩa |
|---|---|
| `inet` | IPv4 address/prefix |
| `inet6` | IPv6 address/prefix |
| `scope host` | Chỉ local host |
| `scope link` | Chỉ local link |
| `scope global` | Scope rộng hơn link, không đồng nghĩa luôn là public Internet |
| `dynamic` | Address được cấp động |

## Route và neighbor

```bash
ip route
ip route get 8.8.8.8
ip neigh
```

| Lệnh | Trả lời câu hỏi |
|---|---|
| `ip route` | Host có những route nào? |
| `ip route get IP` | Kernel thực tế chọn source, gateway và interface nào? |
| `ip neigh` | IP next hop đã ánh xạ sang địa chỉ link chưa? |

Ví dụ đọc route:

```text
default via 192.168.220.2 dev ens33 metric 100
```

| Phần | Ý nghĩa |
|---|---|
| `default` | Khớp khi không route cụ thể hơn |
| `via` | Gateway/next hop |
| `dev` | Interface gửi packet |
| `metric` | Độ ưu tiên giữa route tương đương |

Lệnh nâng cao khi host nhiều bảng route:

```bash
ip rule
ip route show table all
```

## Socket và port

```bash
sudo ss -lntup
sudo ss -lntp 'sport = :18082'
nc -vz -w 3 HOST PORT
curl -v --connect-timeout 3 http://HOST:PORT/
```

| Argument | Ý nghĩa |
|---|---|
| `ss -l` | Listening sockets |
| `ss -n` | Không đổi số thành tên |
| `ss -t` | TCP |
| `ss -u` | UDP |
| `ss -p` | Process sở hữu socket |
| `nc -v` | Verbose |
| `nc -z` | Chỉ scan/kết nối, không gửi dữ liệu ứng dụng |
| `nc -w 3` | Timeout ba giây |
| `curl -v` | Hiện chi tiết kết nối và HTTP |

Xem connection thay vì chỉ listener:

```bash
ss -nt
ss -nt state established
ss -s
```

- `state established`: lọc TCP connection đã thiết lập.
- `ss -s`: tóm tắt socket theo protocol/state.

## Reachability và path

```bash
ping -c 3 HOST
tracepath HOST
traceroute HOST
```

`ping` kiểm tra ICMP reachability, không kiểm tra trực tiếp TCP application port. `tracepath`/`traceroute` giúp quan sát các hop nhưng một số router có thể không phản hồi.

## DNS

```bash
getent ahosts NAME
dig NAME
dig @DNS_SERVER NAME
host NAME
resolvectl status
cat /etc/nsswitch.conf
ls -l /etc/resolv.conf
```

| Lệnh | Trả lời câu hỏi |
|---|---|
| `getent ahosts` | Ứng dụng qua NSS có phân giải được không? |
| `dig` | DNS trả lời thế nào? |
| `dig @SERVER` | DNS server cụ thể trả lời thế nào? |
| `resolvectl status` | Resolver/DNS theo từng link đang dùng gì? |

Một số query hữu ích:

```bash
dig A example.com
dig AAAA example.com
dig -x 192.0.2.10
resolvectl query example.com
```

- `A`: hỏi IPv4 record.
- `AAAA`: hỏi IPv6 record.
- `-x`: reverse lookup IP thành PTR name.

## Persistent configuration

```bash
nmcli device status
nmcli connection show
networkctl list
networkctl status INTERFACE
sudo netplan generate
sudo netplan try
netplan status -a
```

## Packet capture

```bash
sudo tcpdump -ni any host DESTINATION_IP and port PORT
```

Chỉ dùng capture filter đủ hẹp và bảo vệ dữ liệu thu được.

Capture TCP flags khi học handshake:

```bash
sudo tcpdump -ni any 'host DESTINATION_IP and tcp port PORT'
```

Không dùng `-A` hoặc `-X` trên traffic thật nếu không cần payload, vì có thể làm lộ dữ liệu ứng dụng.

## Chuỗi chẩn đoán nhanh

```text
ip link
  ↓
ip addr
  ↓
ip route get
  ↓
ping/tracepath
  ↓
getent/dig
  ↓
ss/nc
  ↓
curl
  ↓
tcpdump nếu vẫn chưa rõ
```

## Nguồn

- [LPIC-1 V5.0 — Topic 109](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [Ubuntu Server — Configuring networks](https://ubuntu.com/server/docs/explanation/networking/configuring-networks/)
