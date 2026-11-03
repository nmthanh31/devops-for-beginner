# N07 Bài 2 — Đọc socket state và capture

> **Sau bài này bạn sẽ:**
> - Đọc `ss -lntp` và các TCP state.
> - Đọc cờ TCP trong `tcpdump`.
> - Viết kết luận **đúng tới lớp mà evidence chứng minh**.
>
> **Cần trước:** [Bài 1](./01-transport-behavior.md).

---

## 1. `ss` — socket trên host

```bash
ss -lntup                     # listening TCP + UDP, có process
ss -nt state established      # kết nối đang mở
```

| Cờ | Ý nghĩa |
|---|---|
| `-l` | Chỉ listening |
| `-n` | IP/port dạng số |
| `-t` / `-u` | TCP / UDP |
| `-p` | Hiện process (cần quyền) |

Ví dụ:

```text
State   Recv-Q Send-Q Local Address:Port  Peer Address:Port Process
LISTEN  0      128    0.0.0.0:18082       0.0.0.0:*         users:(("python3",pid=812,fd=3))
LISTEN  0      128    127.0.0.1:5432      0.0.0.0:*         users:(("postgres",pid=640,fd=5))
```

→ `18082` nhận từ mọi IPv4; `5432` chỉ loopback. Có listener **không** đồng nghĩa firewall cho client từ xa vào.

### TCP state hay gặp

| State | Ở đâu | Ý nghĩa |
|---|---|---|
| `LISTEN` | Server | Đang chờ |
| `SYN-SENT` | Client | Đã gửi SYN, chưa có trả lời — **kẹt ở đây = timeout** |
| `SYN-RECV` | Server | Nhận SYN, đã gửi SYN-ACK, chờ ACK — kẹt nhiều = ACK không về (đường về?) |
| `ESTAB` | Hai bên | Đã thiết lập |
| `TIME-WAIT` | Bên đóng trước | Bình thường |
| `CLOSE-WAIT` | Bên bị đóng | Ứng dụng **chưa gọi close()** — nhiều = bug ứng dụng |

## 2. `tcpdump` — packet trên interface

```bash
sudo tcpdump -ni eth0 'tcp port 18082'
```

```text
10.7.0.10.51000 > 10.7.0.20.18082: Flags [S],  seq 100        ← SYN
10.7.0.20.18082 > 10.7.0.10.51000: Flags [S.], seq 500, ack 101 ← SYN-ACK
10.7.0.10.51000 > 10.7.0.20.18082: Flags [.],  ack 501        ← ACK
10.7.0.20.18082 > 10.7.0.10.51000: Flags [R.], ...            ← RST (nếu bị từ chối)
```

| Cờ | Nghĩa |
|---|---|
| `[S]` | SYN |
| `[S.]` | SYN-ACK (`.` = ACK) |
| `[P.]` | Có dữ liệu (PUSH) |
| `[F.]` | FIN |
| `[R]` / `[R.]` | RST |

`ss` cho biết **socket** trên host; `tcpdump` cho biết **packet** đã qua interface. Hai lớp evidence khác nhau.

## 3. Quy trình khi client timeout

1. Capture client: SYN có rời client?
2. Capture server: SYN có tới?
3. Server có trả SYN-ACK hoặc RST?
4. Client có nhận phản hồi?

UDP timeout không có handshake để theo — nhìn request/response datagram và ICMP error.

## 4. Kết luận đúng tới đâu

Cùng `curl http://VM_IP:18082/`:

| Output | Đã chứng minh | Lớp cần xem |
|---|---|---|
| `Could not resolve host` | Chưa tới mạng | DNS / hostname |
| `Connection refused` | Có RST | Listener, firewall reject |
| `Operation timed out` | Không có phản hồi đúng hạn | Path, firewall drop, đường về |
| `HTTP/1.1 404` | TCP + HTTP server đều đã trả lời | App / path / vhost |
| `HTTP/1.1 503` sau handshake OK | Không còn là lỗi TCP | App / proxy |

### Chọn công cụ theo lớp

| Lệnh | Kiểm tới |
|---|---|
| `nc -vz -w 3 HOST PORT` | TCP connect |
| `curl -v URL` | TCP + TLS + HTTP |

Không dùng một lệnh để tuyên bố mọi lớp đều khỏe.

## Tự kiểm tra

1. Server có hàng trăm socket `SYN-RECV`. Nghi gì?
2. Thấy `Flags [R.]` từ `10.7.0.20` sau SYN. Ai từ chối?
3. App có nhiều `CLOSE-WAIT` tăng dần. Lỗi mạng hay ứng dụng?

<details>
<summary>Đáp án</summary>

1. ACK cuối không về tới server — đường về client sai/bị chặn (hoặc SYN flood).
2. Host/thiết bị mang IP `10.7.0.20` (hoặc firewall giả mạo IP đó với `reject with tcp reset`) — capture ở server để chắc chắn.
3. Ứng dụng — chưa đóng socket sau khi peer đóng.

</details>

## Nguồn

[RFC 9293](https://www.rfc-editor.org/rfc/rfc9293) · [ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html) · [LPIC-1 109.3](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
