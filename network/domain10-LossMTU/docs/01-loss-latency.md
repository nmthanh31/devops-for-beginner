# N10 Bài 1 — Latency, jitter, loss và retransmission

> **Sau bài này bạn sẽ:**
> - Phân biệt RTT, jitter, loss, throughput — bốn hiện tượng khác nhau.
> - Đo **ba lớp** riêng: ICMP RTT, TCP retransmission, thời gian HTTP.
> - Dùng `tc netem` an toàn để mô phỏng delay/loss trong lab.
>
> **Cần trước:** [N07](../../domain07-TCPUDPICMP/README.md) (TCP retransmit).

---

## 1. Bốn khái niệm

| Khái niệm | Nghĩa | Ví dụ triệu chứng |
|---|---|---|
| **Latency / RTT** | Thời gian đi + về | Mọi request đều chậm đều đặn |
| **Jitter** | Độ dao động của delay | Video/voice giật, RTT lúc 20ms lúc 200ms |
| **Packet loss** | Gói không tới / không được phản hồi | Ping mất vài %, TCP retransmit |
| **Throughput** | Dữ liệu truyền được / giây | Tải file chậm |

RTT cao ổn định, jitter cao và loss là **ba bệnh khác nhau**.

## 2. Nguyên nhân hay gặp

Congestion, queue quá dài (bufferbloat), link lỗi, firewall drop, qdisc policy, endpoint quá tải — **hoặc** ứng dụng xử lý chậm dù mạng hoàn toàn ổn.

## 3. Đo ba lớp riêng biệt

| Lớp | Công cụ | Đo được |
|---|---|---|
| ICMP | `ping -c 20 HOST` | RTT min/avg/max/mdev, % loss |
| TCP | `tcpdump` / `ss -ti` | Retransmission, RTT TCP, cwnd |
| HTTP | `curl -w` | Thời gian từng pha |

```bash
curl -o /dev/null -s -w 'dns=%{time_namelookup} tcp=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total}\n' https://example.com/
```

`ttfb − tls` lớn trong khi `tcp` nhỏ → **app chậm**, không phải mạng.

> Ping đo ICMP, đường xử lý/chính sách có thể khác TCP/HTTP. **Không** kết luận từ một mẫu ping — đo nhiều mẫu.

### Đọc retransmission cẩn thận

Capture tại source thấy retransmit = sender **chưa nhận ACK** như mong đợi. Có thể data mất, **hoặc ACK chiều về mất**. Capture hai đầu, so seq/ACK để biết hướng nào lỗi.

> Ping nhỏ tốt nhưng transfer lớn tệ → nghĩ tới **MTU/PMTUD** ([Bài 2](./02-mtu-pmtud.md)), đừng mặc định là bandwidth.

---

## 4. `tc netem` — mô phỏng mạng xấu

`netem` là qdisc thêm delay/loss/duplicate/reorder trên traffic **egress** (đi ra) của interface.

```bash
sudo ip netns exec n10-a tc qdisc add dev veth-a root netem delay 100ms loss 2%
sudo ip netns exec n10-a tc qdisc show dev veth-a
sudo ip netns exec n10-a tc qdisc del dev veth-a root
ip -n n10-a -s link show dev veth-a        # counter TX/RX/dropped
```

**Câu hỏi dự đoán:** delay 100ms chỉ trên **egress của A** → ping từ A tới B RTT tăng bao nhiêu? (Đáp: ~100ms — chỉ chiều A→B bị trễ. Đặt cả hai chiều mới ~200ms.)

> ⚠️ **Không** áp `tc` lên interface SSH/quản trị — VM sẽ mất kết nối. Chỉ trên veth trong namespace.

### Quy trình lab

baseline → thêm netem → đo nhiều mẫu + capture → **xóa qdisc** → đo lại (chứng minh nhân quả).

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Request chậm = mạng chậm." | Đo `curl -w` để tách app. |
| "Retransmit = data bị mất." | Có thể ACK chiều về mất. |
| "1 ping 300ms → mạng tệ." | Cần nhiều mẫu. |
| "netem tác động cả hai chiều." | Chỉ egress của interface đó. |

## Tự kiểm tra

1. `curl -w`: `tcp=0.002 tls=0.010 ttfb=2.500`. Lỗi ở đâu?
2. Ping 20 mẫu: avg 40ms, mdev 35ms, loss 0%. Bệnh gì?

<details>
<summary>Đáp án</summary>

1. Ứng dụng xử lý chậm (sau TLS đến byte đầu 2.5s), mạng nhanh.
2. Jitter cao (mdev lớn), không có loss.

</details>

## Nguồn

[tc-netem(8)](https://man7.org/linux/man-pages/man8/tc-netem.8.html) · [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293) · [curl write-out](https://everything.curl.dev/usingcurl/verbose/writeout)
