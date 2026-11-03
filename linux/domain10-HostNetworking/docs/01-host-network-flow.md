# Bài 1 — Luồng packet trên Linux host

## Mục tiêu

Sau bài này, bạn phải vẽ được đường đi tổng quát:

```text
program → process → socket → kernel network stack
        → route → interface → NIC → network → remote host
```

Bài này định nghĩa các thành phần tổng quan. Những bài sau đi sâu từng nhóm mà không lặp lại toàn bộ phần này.

## 1. Từ program đến kernel

### Program và process

**Program** là code có thể thực thi, ví dụ `/usr/bin/curl`. Khi program được chạy, hệ điều hành tạo một **process**. Process có PID, user, memory, environment, current working directory và file descriptor.

Program nằm trên disk chưa gửi được network traffic. Process đang chạy mới thực hiện yêu cầu giao tiếp.

### Kernel và system call

**Kernel** là lõi hệ điều hành, quản lý process, memory, device và network. Process chạy ở user space không trực tiếp điều khiển NIC. Nó dùng **system call** để yêu cầu kernel làm việc.

Các system call network thường gặp về mặt khái niệm:

- `socket()`: tạo socket;
- `connect()`: bắt đầu kết nối tới remote endpoint;
- `bind()`: gắn socket với local IP và port;
- `listen()`/`accept()`: nhận TCP connection;
- `send()`/`recv()`: gửi và nhận dữ liệu.

### File descriptor và socket

**File descriptor (FD)** là số nguyên process dùng để tham chiếu tài nguyên kernel đã mở. File, pipe và socket đều có thể được truy cập qua FD.

**Socket** là đối tượng giao tiếp do kernel quản lý. Nó nối process với network stack và có thể chứa protocol, local IP:port, remote IP:port cùng trạng thái connection.

```text
process PID 1234
   └── fd 3
         └── TCP socket 192.168.220.133:18082
```

## 2. Tên, địa chỉ và endpoint

### Hostname, resolver và DNS

**Hostname** là tên dùng để nhận diện host, ví dụ `k8s-wk`. Network routing cần địa chỉ IP, nên khi application dùng tên, **resolver** phải tìm IP tương ứng. **DNS** là một nguồn dữ liệu resolver thường sử dụng; `/etc/hosts` có thể là nguồn khác.

DNS chỉ giải quyết bước tên → IP. Có IP rồi vẫn còn route, firewall, socket và application.

### IP address

**IP address** là địa chỉ logic ở lớp network:

- **source IP:** địa chỉ phía gửi trong packet;
- **destination IP:** địa chỉ packet cần tới.

IP giúp đưa packet tới đúng host qua một hoặc nhiều router.

### Port và endpoint

**Port** là số TCP/UDP từ `0` đến `65535`. IP đưa packet tới host; port giúp kernel đưa dữ liệu tới đúng socket/process trên host đó.

**Endpoint** thường được mô tả bằng protocol + IP + port:

```text
TCP 192.168.220.133:18082
```

## 3. Kernel chọn đường đi

### Routing table và route

**Routing table** là tập các route trong kernel. Nó trả lời:

```text
Muốn tới destination IP này thì packet phải đi đâu tiếp theo?
```

**Route** là một quy tắc trong bảng, thường gồm destination prefix, interface đầu ra và có thể có gateway, metric hoặc source IP ưu tiên.

Kernel so destination IP với các route, chọn route phù hợp nhất rồi xác định:

- source IP;
- interface đầu ra;
- gửi trực tiếp hay qua gateway.

### Interface, driver và NIC

**Network interface** là đối tượng network kernel nhìn thấy, ví dụ `ens33` hoặc `lo`. IP và MTU được gắn vào interface.

**Driver** là code kernel điều khiển thiết bị. **NIC** là card mạng thật hoặc virtual network adapter.

```text
kernel network stack → interface → driver → NIC
```

### Gateway và next hop

**Gateway** là router trên local network có thể chuyển packet sang network khác. **Next hop** là thiết bị kế tiếp mà host trực tiếp giao packet; nó có thể là gateway hoặc chính destination nếu destination cùng local subnet.

## 4. Từ IP packet thành frame

### MAC và neighbor

**MAC address** là địa chỉ lớp link dùng trên local Ethernet network.

**Neighbor** là host/router reachable trực tiếp trên cùng link. Kernel cần ánh xạ IP của next hop sang MAC. IPv4 thường dùng ARP; IPv6 dùng Neighbor Discovery.

### Packet và frame

**IP packet** chứa source/destination IP. **Ethernet frame** chứa source/destination MAC và mang IP packet làm payload.

```text
application data
   ↓ thêm TCP/UDP header
segment/datagram
   ↓ thêm IP header
IP packet
   ↓ thêm Ethernet header
frame
```

Quá trình thêm lớp gọi là **encapsulation**. Máy nhận tháo các lớp theo chiều ngược lại, gọi là **decapsulation**.

### Switch và router

- **Switch** chuyển frame trong cùng Layer-2 network dựa trên MAC.
- **Router** chuyển IP packet giữa các network dựa trên route.

Mỗi router thường bỏ frame của link cũ và tạo frame mới cho link tiếp theo. IP source/destination thường giữ nguyên, trừ khi có NAT.

## 5. Firewall, NAT và VMware network

**Firewall** kiểm tra packet theo rule rồi accept, drop hoặc reject. Nó có thể nằm trên VM, Windows host, VMware/hypervisor hoặc thiết bị mạng.

**NAT** thay đổi source/destination IP hoặc port. Với VMware NAT, VM thường dùng private IP và đi ra ngoài thông qua cơ chế NAT của VMware/host.

Các mode thường gặp:

- **NAT:** VM dùng mạng private và đi ra ngoài qua NAT;
- **Bridged:** VM xuất hiện gần như một host trực tiếp trên LAN;
- **Host-only:** VM chủ yếu giao tiếp với host và các VM cùng mạng riêng.

## 6. Luồng outbound hoàn chỉnh

Giả sử process chạy:

```bash
curl http://example.com:80/
```

Luồng:

1. Shell tạo process `curl`.
2. Resolver đổi `example.com` thành destination IP.
3. Process tạo TCP socket và yêu cầu connect tới IP:80.
4. Kernel chọn source IP và source port tạm thời.
5. Kernel tra routing table để chọn interface và next hop.
6. Kernel tìm MAC của next hop nếu neighbor table chưa có.
7. TCP segment được bọc trong IP packet rồi Ethernet frame.
8. Driver đưa frame cho NIC.
9. Switch/router chuyển traffic tới remote host.
10. Remote kernel đưa traffic tới socket đang listen port 80.

## 7. Luồng inbound hoàn chỉnh

Giả sử Windows truy cập `192.168.220.133:18082`:

1. Windows chọn route tới IP VM.
2. Frame tới virtual NIC của VM.
3. Driver đưa packet vào kernel VM.
4. Kernel xác định destination IP là local.
5. Firewall quyết định accept/drop/reject.
6. TCP tìm listening socket khớp IP:18082.
7. Nếu có listener, process nhận connection.
8. Nếu không có listener, client thường nhận `Connection refused`.
9. Nếu packet bị drop hoặc phản hồi không quay về, client thường timeout.

## 8. Bề mặt quan sát

| Câu hỏi | Công cụ |
|---|---|
| Interface và IP là gì? | `ip link`, `ip addr` |
| Kernel chọn đường nào? | `ip route get` |
| Tên được phân giải ra sao? | `getent`, `dig`, `resolvectl` |
| Process nào listen? | `ss -lntup` |
| Packet có thực sự xuất hiện? | `tcpdump` |

<!-- learn:tail -->
## Tự kiểm tra

1. Process gọi `connect()` tới `10.0.0.5:443`. Kernel cần quyết định những gì trước khi packet rời NIC?
2. Một inbound SYN tới port 8080 nhưng không có socket listen. Kernel làm gì?

<details>
<summary>Đáp án</summary>

1. Route (interface, next hop, source IP) → neighbor (MAC next hop) → source port tạm → (firewall output) → đóng frame.
2. Trả RST (client thấy `Connection refused`), trừ khi firewall drop trước.

</details>

## Nguồn

- [LPIC-1 V5.0 — Topic 109](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

