# N01 Lab — Quan sát đóng gói bằng capture

| | |
|---|---|
| **Thời lượng** | 45–60 phút |
| **Môi trường** | VM lab Linux có `iproute2`, `tcpdump`; quyền `sudo` |
| **Mục tiêu** | Dự đoán rồi chứng minh bằng capture: frame ping gateway mang MAC nào, IP nào; vì sao ARP không có port |
| **Không làm** | Không đổi IP/route của interface đang dùng SSH |

---

## Bước 0 — Ghi baseline

```bash
ip -br link
ip -br addr
ip route
```

Điền bảng (đặt tên interface lab là `IFACE`, gateway là `GW`):

| Mục | Giá trị |
|---|---|
| Interface ra mạng (`IFACE`) | |
| IP/prefix của VM | |
| MAC của VM | |
| Gateway (`GW`) | |

## Bước 1 — Dự đoán (viết ra trước khi chạy)

```bash
ip route get <GW>
```

Trả lời vào notes:

1. Ping `GW` thì ICMP frame có **destination MAC** là của ai?
2. Trước ICMP, sẽ thấy gói gì? (gợi ý: N02)
3. Nếu ping một IP **ngoài subnet** (ví dụ `1.1.1.1`), destination MAC là của ai?

## Bước 2 — Capture

Terminal 1:

```bash
sudo ip neigh flush dev <IFACE>   # xóa cache ARP để chắc chắn thấy ARP mới
sudo tcpdump -eni <IFACE> -c 20 'arp or icmp'
```

> `ip neigh flush` chỉ xóa cache tạm, kernel tự học lại ngay. Nếu đang SSH qua `IFACE`, phiên có thể khựng 1–2 giây — bình thường.

Terminal 2:

```bash
ping -c 2 <GW>
ping -c 2 1.1.1.1
```

### Kết quả mong đợi (dạng)

```text
... <MAC VM> > ff:ff:ff:ff:ff:ff, ethertype ARP, Request who-has <GW> tell <IP VM>
... <MAC GW> > <MAC VM>,          ethertype ARP, Reply <GW> is-at <MAC GW>
... <MAC VM> > <MAC GW>,          ethertype IPv4, <IP VM> > <GW>: ICMP echo request
... <MAC GW> > <MAC VM>,          ethertype IPv4, <GW> > <IP VM>: ICMP echo reply
... <MAC VM> > <MAC GW>,          ethertype IPv4, <IP VM> > 1.1.1.1: ICMP echo request
```

Nhận xét điều cần thấy: gói tới `1.1.1.1` vẫn có **destination MAC = MAC gateway**.

> Nếu gateway chặn ping: vẫn thấy ARP và *echo request* rời VM — đủ chứng minh VM đã gửi đúng.

## Bước 3 — So sánh với loopback

```bash
sudo tcpdump -eni lo -c 4 icmp &
ping -c 2 127.0.0.1
```

Quan sát: không có ARP, MAC toàn `00:00:00:00:00:00`. Giải thích vì sao (loopback không có link Ethernet thật, không cần tìm next hop).

## Bước 4 — Giải thích (5 dòng)

Viết 5 dòng trả lời:

1. Vì sao ARP request có destination `ff:ff:ff:ff:ff:ff`?
2. Vì sao ARP không có port?
3. Vì sao ping `1.1.1.1` lại dùng MAC của gateway?
4. Capture `lo` khác `IFACE` ở điểm nào, vì sao?
5. Nếu không thấy gì trong capture, bạn kiểm gì đầu tiên?

---

## Definition of Done

- [ ] Bảng baseline đầy đủ.
- [ ] Dự đoán viết **trước** khi capture, có đánh dấu đúng/sai.
- [ ] Capture có ARP request, ARP reply, ICMP request (reply nếu gateway cho phép).
- [ ] Chỉ ra được dòng chứng minh "IP đích ngoài subnet → MAC đích là gateway".
- [ ] 5 dòng giải thích.
- [ ] Nếu đưa evidence lên repo public: đã che MAC/IP nội bộ.

## Cleanup

Lab này không tạo tài nguyên. Dừng `tcpdump` chạy nền nếu còn: `sudo pkill -f 'tcpdump -eni lo'`.
