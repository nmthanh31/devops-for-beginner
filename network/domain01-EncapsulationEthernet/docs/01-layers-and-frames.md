# N01 Bài 1 — Các lớp và đóng gói (encapsulation)

> **Sau bài này bạn sẽ:**
> - Giải thích vì sao một request cần đồng thời **MAC, IP và port**.
> - Vẽ được quá trình đóng gói (đi xuống) và tháo gói (đi lên) của một HTTP request.
> - Dùng mô hình lớp để chọn đúng lệnh khi debug, thay vì chạy mọi lệnh cùng lúc.
>
> **Cần trước:** [L10 — host network flow](../../../linux/domain10-HostNetworking/docs/01-host-network-flow.md).

---

## 1. Hình dung: gửi một bưu kiện

Bạn gửi một món quà (dữ liệu) cho bạn ở thành phố khác:

| Đời thực | Mạng | Trả lời câu hỏi |
|---|---|---|
| Món quà | HTTP request | Nội dung là gì? |
| Ghi "gửi phòng 8080" | **TCP port** | Giao cho *ứng dụng* nào trên máy đích? |
| Địa chỉ nhà người nhận | **IP address** | Giao tới *máy* nào trên Internet? |
| Xe shipper chặng hiện tại | **MAC address** | Chặng *này* giao cho thiết bị nào? |

Chú ý dòng cuối: mỗi chặng đổi xe shipper (MAC đổi), nhưng địa chỉ nhà trên bưu kiện (IP) giữ nguyên. Đây là ý quan trọng nhất của bài.

---

## 2. Đi xuống: đóng gói từng lớp

Giả sử bạn mở `http://10.66.10.12:8080/` từ máy `10.66.10.11`:

```text
 Lớp             Thêm gì                                  Đơn vị gọi là
 ───────────────────────────────────────────────────────────────────────
 Application     "GET / HTTP/1.1 ..."                     message
      ▼
 Transport (TCP) src port 49152 → dst port 8080,          segment
                 sequence, flags
      ▼
 Network (IP)    src 10.66.10.11 → dst 10.66.10.12, TTL   packet
      ▼
 Link (Ethernet) src MAC → dst MAC (next hop), EtherType  frame
      ▼
 Physical        tín hiệu điện / sóng / ảo hóa trên link
```

- **Encapsulation** = thêm header khi đi xuống. Payload của lớp dưới là *toàn bộ* đơn vị dữ liệu của lớp trên.
- **Source port `49152`** là port tạm thời (ephemeral) do OS chọn, để phân biệt kết nối này với các kết nối khác.

```text
┌──────────┬────────┬─────────┬────────────────┐
│ Ethernet │   IP   │   TCP   │  HTTP payload  │
│  header  │ header │ header  │                │
└──────────┴────────┴─────────┴────────────────┘
 ◄───────────────── frame ─────────────────────►
            ◄────────── packet ────────────────►
                     ◄────── segment ──────────►
```

## 3. Đi lên: tháo gói ở máy nhận

Mỗi lớp nhìn **một trường** để biết giao payload cho ai ở lớp trên:

```text
NIC nhận frame hợp lệ
  → EtherType   (0x0800 = IPv4, 0x86DD = IPv6) → giao cho IP
  → IP protocol (6 = TCP, 17 = UDP, 1 = ICMP)  → giao cho TCP/UDP
  → dst port    (8080)                          → tìm socket đang listen
  → process đọc bytes từ socket
```

**Hệ quả thực tế:** `systemctl status app` báo `active` nhưng process không listen, hoặc chỉ bind `127.0.0.1`, thì bước cuối không tìm được socket → request vẫn fail. "Service chạy" ≠ "service nhận được request".

---

## 4. Mỗi địa chỉ trả lời một câu hỏi

| Địa chỉ | Câu hỏi | Phạm vi | Có đổi dọc đường không? |
|---|---|---|---|
| **MAC** | Frame giao cho interface nào trên *link hiện tại*? | Một link | **Có** — đổi ở mỗi router hop |
| **IP** | Packet cần tới *host* nào? | End-to-end | Thường **không** (trừ NAT) |
| **Port** | *Socket/process* nào nhận? | Trong một host | Thường **không** (trừ NAT/proxy) |

**Frame chỉ sống trên một link.** Router nhận frame → bóc lấy IP packet → chọn next hop → bọc vào **frame mới**. Đồng thời router giảm **TTL** (IPv6: Hop Limit) đi 1 để packet không chạy vòng mãi.

```text
   A ───────── link 1 ───────── Router ───────── link 2 ───────── B
 Ethernet:  MAC A → MAC R1                 MAC R2 → MAC B      ← đổi
 IP:        IP A  → IP B                   IP A  → IP B        ← giữ
 TCP:       53000 → 80                     53000 → 80          ← giữ
```

Khi so hai bản capture ở hai link, **MAC khác nhau là bình thường** — đó chính là routing đang hoạt động đúng.

---

## 5. Ethernet frame

Ethernet header gồm 3 trường chính:

| Trường | Ý nghĩa |
|---|---|
| Destination MAC | Interface nhận trên link này |
| Source MAC | Interface gửi |
| EtherType | Payload là IPv4, IPv6, ARP (`0x0806`)… |

Cuối frame có phần kiểm lỗi (FCS). Frame hỏng bị **loại tại link đó** — đây không phải cơ chế gửi lại; việc gửi lại (reliability) là của TCP.

## 6. MTU — giới hạn kích thước

**MTU** (Maximum Transmission Unit) là kích thước IP packet tối đa một interface truyền được trên link. Header các lớp chiếm chỗ, nên dữ liệu ứng dụng nhỏ hơn MTU.

```text
MTU 1500 (Ethernet thông thường)
 − 20 byte IPv4 header (không options)
 − 20 byte TCP header  (không options)
 = 1460 byte TCP data tối đa trong một packet
```

Đây là phép tính minh họa, **không phải hằng số**: TCP options, IPv6 (header 40 byte), tunnel/VPN đều làm con số nhỏ đi. Path MTU học ở [N10](../../domain10-LossMTU/README.md).

---

## 7. Suy luận như người vận hành

Đọc thông báo lỗi để biết request **đã đi tới lớp nào**:

| Triệu chứng | Đã qua được | Kiểm tiếp |
|---|---|---|
| `Could not resolve host` | Chưa tạo được TCP connection | DNS ([N06](../../domain06-DHCPDNSTime/README.md)) |
| `Connection timed out` | Đã có IP đích | Route, neighbor/ARP, firewall, capture |
| `Connection refused` | Packet tới được host | Listener/port ([N07](../../domain07-TCPUDPICMP/README.md)) |
| HTTP `404` | Mạng + TCP + HTTP server đều ổn | Virtual host, path, ứng dụng |

Phân tầng giúp **chọn lệnh theo câu hỏi**: lỗi DNS thì đừng `tcpdump` cổng 80; lỗi 404 thì đừng sửa route.

## 8. Lệnh lấy bằng chứng

```bash
ip -d link show ens33          # MAC (link/ether), MTU, trạng thái
sudo tcpdump -eni ens33 -c 10  # -e hiện Ethernet header (MAC)
```

Lưu ý: capture với `-i any` dùng dạng "cooked capture" (Linux SLL), **không phải Ethernet header gốc** — muốn thấy MAC thật, capture trên interface cụ thể.

---

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "MAC đích là MAC của server cuối cùng." | MAC đích là của **next hop** trên link hiện tại; khác subnet thì là MAC gateway. |
| "IP đổi ở mỗi router." | IP giữ nguyên; chỉ NAT/proxy mới đổi. Thứ đổi ở mỗi hop là MAC và TTL. |
| "Service `active` nghĩa là nhận được request." | Còn cần listener đúng IP/port. |
| "Frame lỗi thì Ethernet tự gửi lại." | Ethernet chỉ loại bỏ; TCP mới gửi lại. |

## Tự kiểm tra

1. A (`10.1.1.10/24`) gửi tới B (`10.2.2.20`) qua gateway `10.1.1.1`. Trên link đầu tiên, destination MAC là của ai? Destination IP là gì?
2. Vì sao một máy cần cả MAC lẫn IP, sao không chỉ dùng một?
3. `curl` báo `Connection refused`. Có nên kiểm route trước không?
4. MTU 1500, dùng IPv6 không options, TCP không options: tối đa bao nhiêu byte TCP data?

<details>
<summary>Đáp án</summary>

1. MAC của **gateway** `10.1.1.1`; IP đích vẫn là **`10.2.2.20`**.
2. MAC chỉ có nghĩa trên một link (giao chặng hiện tại); IP định danh host end-to-end để router chọn đường qua nhiều link.
3. Không ưu tiên. `refused` nghĩa là host đích đã nhận SYN và trả RST — route đã tới nơi. Kiểm listener/port trên server.
4. 1500 − 40 − 20 = **1440** byte.

</details>

## Nguồn

- [RFC 791 — IPv4](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 9293 — TCP](https://www.rfc-editor.org/rfc/rfc9293)
