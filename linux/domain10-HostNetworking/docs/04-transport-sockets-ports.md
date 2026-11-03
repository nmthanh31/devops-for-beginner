# Bài 4 — TCP, UDP, socket và port

## Mục tiêu và tiền đề

Bài 3 đã đưa IP packet tới đúng host. Bài này giải thích kernel đưa dữ liệu tới đúng process bằng transport protocol, port và socket.

Đọc trước: [Routing table, gateway và neighbor](./03-routing-gateway-neighbor.md).

## 1. Transport layer

Transport layer nằm giữa application và IP. IP xác định host; transport layer xác định giao tiếp process-to-process.

Hai protocol chính:

- TCP;
- UDP.

ICMP thuộc lớp network/control, không dùng TCP/UDP port, nhưng được đặt cạnh đây để phân biệt.

## 2. TCP

TCP là protocol hướng connection, cung cấp:

- byte stream có thứ tự;
- acknowledgment;
- retransmission khi suy đoán mất dữ liệu;
- flow control để không làm bên nhận quá tải;
- congestion control để điều chỉnh theo network path.

HTTP/HTTPS và SSH thường dùng TCP.

### Three-way handshake

```text
client                     server
  | -------- SYN --------> |
  | <----- SYN,ACK --------|
  | -------- ACK --------> |
  |      ESTABLISHED       |
```

- `SYN`: yêu cầu bắt đầu connection;
- `SYN,ACK`: server đồng ý và xác nhận;
- `ACK`: client xác nhận bước cuối.

Nếu không có listener, server host thường trả `RST`, client thấy `Connection refused`. Nếu packet/reply bị drop, client retransmit rồi timeout.

## 3. UDP

UDP gửi từng datagram độc lập. Nó không có TCP handshake và không tự bảo đảm delivery, thứ tự hay retransmission.

Application dùng UDP phải tự quyết định có cần retry, sequence hoặc acknowledgment không. DNS query thông thường thường dùng UDP nhưng DNS cũng có thể dùng TCP.

## 4. ICMP

ICMP truyền thông tin điều khiển và lỗi như:

- Echo request/reply cho `ping`;
- destination unreachable;
- packet too big.

Ping thất bại không chứng minh TCP port thất bại, vì ICMP có thể bị chặn riêng.

## 5. Port, endpoint và connection

**Port** là số 16-bit giúp kernel phân biệt socket TCP/UDP trên cùng host.

**Endpoint**:

```text
protocol + IP + port
```

Một TCP connection được phân biệt bằng hai endpoint:

```text
source IP:source port ↔ destination IP:destination port
```

Client thường dùng **ephemeral source port** do kernel chọn. Server dùng port service ổn định như 22, 80, 443 hoặc 18082 trong lab.

`/etc/services` ánh xạ tên service với port quy ước; nó không chứng minh service đang chạy.

## 6. Socket và file descriptor

Socket là kernel object. Process tham chiếu socket bằng file descriptor.

### Vòng đời server

```text
socket() → bind() → listen() → accept() → send/recv → close()
```

- `bind`: gắn local IP:port;
- `listen`: chờ TCP connection;
- `accept`: tạo socket riêng cho một connection đã tới.

### Vòng đời client

```text
socket() → connect() → send/recv → close()
```

`connect()` với TCP khởi động handshake tới remote endpoint.

## 7. Bind address

Bind address quyết định traffic gửi tới local address nào có thể khớp listener:

| Bind | Ý nghĩa |
|---|---|
| `127.0.0.1:18082` | Chỉ IPv4 loopback local |
| `192.168.220.133:18082` | Chỉ IP VM đó |
| `0.0.0.0:18082` | Mọi local IPv4 address |
| `[::1]:18082` | Chỉ IPv6 loopback |
| `[::]:18082` | Mọi local IPv6 address; dual-stack tùy cấu hình |

Ví dụ:

```bash
python3 -m http.server 18082 --bind 127.0.0.1
```

Windows không kết nối được qua IP VM vì listener chỉ khớp loopback.

```bash
python3 -m http.server 18082 --bind 0.0.0.0
```

Listener nhận traffic gửi tới các local IPv4 address, nhưng route, VMware network và firewall vẫn phải cho phép.

`0.0.0.0` là wildcard để bind, không phải địa chỉ client nhập vào trình duyệt.

## 8. Quan sát socket

```bash
sudo ss -lntup
sudo ss -lntp 'sport = :18082'
```

- `-l`: listening;
- `-n`: giữ dạng số;
- `-t`: TCP;
- `-u`: UDP;
- `-p`: process sở hữu socket.

## 9. Trạng thái TCP thường gặp

- `LISTEN`: chờ connection mới;
- `SYN-SENT`: client đã gửi SYN;
- `SYN-RECV`: server đã nhận SYN;
- `ESTAB`: connection đã thiết lập;
- `TIME-WAIT`: connection đã đóng nhưng kernel còn giữ trạng thái tạm;
- `CLOSE-WAIT`: remote đã đóng nhưng local process chưa close;
- `FIN-WAIT-*`: local đã bắt đầu đóng connection.

Một trạng thái chỉ trở thành evidence có ý nghĩa khi được liên hệ với số lượng, thời gian và triệu chứng ứng dụng.

## 10. Kiểm tra transport và application

```bash
nc -vz -w 3 192.168.220.133 18082
curl -v --connect-timeout 3 http://192.168.220.133:18082/
```

`nc` kiểm tra mở TCP connection. `curl` kiểm tra thêm protocol HTTP. `nc` thành công chưa chứng minh HTTP response đúng.

<!-- learn:tail -->
## Tự kiểm tra

1. `ss -lntp` thấy `127.0.0.1:8080`. Windows gọi `VM_IP:8080` ra gì?
2. Vì sao `ping` OK không chứng minh port 8080 mở?

<details>
<summary>Đáp án</summary>

1. `Connection refused` (không có socket khớp IP đích), trừ khi firewall drop → timeout.
2. ICMP không dùng port; TCP 8080 cần listener + firewall cho phép.

</details>

## Nguồn

- [LPIC-1 V5.0 — Objectives 109.1 và 109.3](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

