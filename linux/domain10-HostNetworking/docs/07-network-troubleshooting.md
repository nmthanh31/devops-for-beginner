# Bài 7 — Quy trình network troubleshooting

## Mục tiêu và tiền đề

Bài này không định nghĩa lại interface, route, DNS và socket. Nó dùng các khái niệm của Bài 1–6 để xây dựng quy trình điều tra.

## 1. Symptom, hypothesis, evidence và root cause

- **Symptom:** biểu hiện quan sát được, ví dụ timeout.
- **Hypothesis:** giả thuyết có thể kiểm tra, ví dụ service chỉ bind loopback.
- **Evidence:** command output, log, config hoặc packet capture gắn với thời điểm.
- **Root cause:** nguyên nhân giải thích được symptom và evidence.

Mẫu làm việc:

```text
Question   → đang muốn biết gì?
Prediction → nếu giả thuyết đúng sẽ thấy gì?
Command    → công cụ nào quan sát đúng lớp?
Result     → output thực tế?
Decision   → giữ hay loại giả thuyết?
```

Restart làm lỗi biến mất chưa chắc chứng minh root cause; nó có thể chỉ xóa trạng thái cần điều tra.

## 2. Xác định flow thật

Ghi rõ:

```text
source host/IP → destination name/IP:port
protocol/application
timestamp
error chính xác
```

Ví dụ:

```text
Windows 192.168.220.1
→ VM 192.168.220.133:18082/TCP
→ HTTP
→ Connection refused
```

Test trên chính server không chứng minh remote client truy cập được, vì source, route, DNS và firewall path khác nhau.

## 3. Quy trình từ gần đến xa

### Bước 1 — Link/interface

```bash
ip -br link
```

Hỏi: interface có `UP`, `LOWER_UP` không? Với VM, virtual NIC có connected và đúng VMware mode không?

### Bước 2 — Address/prefix

```bash
ip -br addr
```

Hỏi: host có đúng IP và prefix không? Prefix sai có thể làm host nhầm destination on-link hay phải qua gateway.

### Bước 3 — Route

```bash
ip route
ip route get DESTINATION_IP
```

Hỏi: kernel chọn đúng `src`, `via`, `dev` không?

### Bước 4 — Neighbor/gateway

```bash
ip neigh
ping -c 3 GATEWAY_IP
```

Hỏi: next hop có phân giải được không? Neighbor `FAILED` khiến packet không rời local link đúng cách.

Ping có thể bị chặn, nên phải đối chiếu route và neighbor thay vì kết luận chỉ từ ping.

### Bước 5 — Remote IP/path

```bash
ping -c 3 REMOTE_IP
tracepath REMOTE_IP
```

Hỏi: IP reachability/path có dấu hiệu lỗi không? Một số router không trả lời traceroute/ICMP nên dấu `*` không tự động là root cause.

### Bước 6 — Name resolution

```bash
getent ahosts NAME
dig NAME
resolvectl status
```

Hỏi: lỗi nằm ở DNS/NSS hay connection sau khi đã có IP?

### Bước 7 — Listener và TCP/UDP port

Trên server:

```bash
sudo ss -lntup
```

Từ client:

```bash
nc -vz -w 3 DESTINATION_IP PORT
```

Hỏi: listener có bind đúng destination IP:port không? `127.0.0.1:18082` không khớp traffic gửi tới `192.168.220.133:18082`.

### Bước 8 — Application protocol

```bash
curl -v --connect-timeout 3 http://DESTINATION_IP:PORT/
```

Hỏi: TCP mở được nhưng HTTP response có đúng không?

### Bước 9 — Packet capture

Khi các bề mặt trên chưa đủ:

```bash
sudo tcpdump -ni any 'host DESTINATION_IP and tcp port PORT'
```

Packet capture có thể chứa dữ liệu nhạy cảm. Capture đúng host/port/thời gian và tránh payload nếu không cần.

## 4. Đọc lỗi phổ biến

| Lỗi | Giả thuyết đầu tiên | Chưa được phép kết luận |
|---|---|---|
| `Could not resolve host` | name resolution | route tới service hỏng |
| `Network is unreachable` | thiếu route/interface không dùng được | remote service down |
| `Connection refused` | host reachable nhưng thiếu listener hoặc explicit reject | packet bị drop im lặng |
| `Connection timed out` | drop/path/return path/service không phản hồi | firewall chắc chắn là nguyên nhân |
| `No route to host` | route/neighbor/ICMP unreachable | chỉ có một nguyên nhân duy nhất |

Thông báo lỗi giúp tạo hypothesis, không phải kết luận cuối.

## 5. Đọc TCP handshake bằng packet evidence

### Server không thấy SYN

Lỗi nằm trước server hoặc capture sai interface/filter: client route, VMware network, upstream firewall/path.

### Server thấy SYN và trả RST

Host đã nhận packet nhưng thường không có listener phù hợp hoặc có explicit reject.

### Server thấy SYN nhưng không trả SYN-ACK/RST

Kiểm tra local firewall, kernel/socket và khả năng phản hồi.

### Handshake hoàn tất nhưng HTTP lỗi

Transport path hoạt động. Chuyển sang application config, endpoint, permission và log.

## 6. Forward path và return path

TCP cần hai chiều:

```text
client → server  forward path
server → client  return path
```

Traffic đi đúng nhưng return route sai vẫn gây timeout. **Asymmetric routing** là trường hợp hai chiều đi qua các đường khác nhau; nó có thể gây lỗi với stateful firewall hoặc NAT.

## 7. Một test không chứng minh mọi lớp

| Test thành công | Đã chứng minh | Chưa chứng minh |
|---|---|---|
| `ping IP` | ICMP echo có phản hồi | TCP port/application hoạt động |
| `dig NAME` | DNS server trả lời | NSS/application dùng cùng kết quả |
| `nc HOST PORT` | TCP connection mở được | HTTP/API trả nội dung đúng |
| `curl URL` | HTTP path đó hoạt động từ client đó | mọi client đều truy cập được |
| `ss -lntp` | server có local listener | remote route/firewall đúng |

## 8. Verify sau khi sửa

- **Positive test:** luồng hợp lệ hoạt động, ví dụ nhận đúng HTTP 200.
- **Negative test:** port/endpoint không được phép vẫn bị từ chối đúng.
- **Persistence test:** cấu hình còn đúng sau restart/reboot có kiểm soát.

Evidence tối thiểu:

```text
ip -br link
ip -br addr
ip route get DESTINATION_IP
resolver evidence nếu dùng tên
ss listener evidence
client connection/application test
```

<!-- learn:tail -->
## Tự kiểm tra

Windows `Test-NetConnection VM -Port 8080` → `TcpTestSucceeded: False`. Trên VM, `ss` có `0.0.0.0:8080`, `curl 127.0.0.1:8080` OK. Ba giả thuyết và lệnh kiểm từng cái?

<details>
<summary>Đáp án</summary>

1. Firewall VM chặn → `sudo ufw status` / `nft list ruleset`; capture `tcpdump -ni ens33 port 8080` xem SYN có tới.
2. Windows tới sai IP/sai mạng VMware → `ipconfig`, `ip -br addr` trên VM, `Test-NetConnection` ping.
3. Đường về sai (VM có route khác cho IP Windows) → `ip route get <IP-Windows>`.

</details>

## Nguồn

- [LPIC-1 V5.0 — Objectives 109.3 và 109.4](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

