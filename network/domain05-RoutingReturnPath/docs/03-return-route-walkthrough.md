# N05 Ví dụ — SYN tới server, SYN-ACK đi sai đường

## Bối cảnh

```text
Client 10.51.1.10/24 ── 10.51.1.1 [Router] 10.52.1.1 ── Server 10.52.1.20/24
                                                        default via 10.52.1.254
                                                        (một router khác, không có đường tới 10.51.1.0/24)
```

- Client: `10.52.1.0/24 via 10.51.1.1` ✅
- Server: **không** có route về `10.51.1.0/24`, chỉ có default route tới một gateway khác.

Triệu chứng: `curl http://10.52.1.20:8080` từ client → **timeout**.

> ✋ Dự đoán: capture ở server sẽ thấy gì? Ở client thấy gì?

---

## Điều tra

| Bước | Ở đâu | Lệnh | Kết quả |
|---|---|---|---|
| 1 | Client | `ip route get 10.52.1.20` | `via 10.51.1.1` ✅ |
| 2 | Server | `ss -lntp` | Có listener `:8080` ✅ |
| 3 | Server | `tcpdump -ni eth0 port 8080` | SYN **đến**, SYN-ACK **đi ra** |
| 4 | Router (egress phía client) | `tcpdump` | **Không** thấy SYN-ACK |
| 5 | Server | `ip route get 10.51.1.10` | `via 10.52.1.254` ❌ — gateway sai |

Kết luận: chiều đi đúng; server gửi SYN-ACK cho gateway sai → không quay về router → client timeout.

## Sửa tối thiểu

```bash
# Trong namespace server (lab)
ip route add 10.51.1.0/24 via 10.52.1.1
```

## Verify

1. Server: `ip route get 10.51.1.10` → `via 10.52.1.1`.
2. Capture router thấy SYN-ACK đi về client.
3. `curl` thành công (positive).
4. Negative: xóa đúng route đó → lỗi tái hiện → thêm lại.

## Vì sao không bật NAT để "chữa"?

SNAT trên router (đổi source thành `10.52.1.1`) cũng làm reply về được, nhưng **đổi semantics của flow**: server không còn thấy IP client thật, log/ACL sai. Nó che triệu chứng chứ không sửa nguyên nhân nếu yêu cầu là routing thuần.
