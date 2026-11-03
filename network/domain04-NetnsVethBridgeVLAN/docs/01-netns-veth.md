# N04 Bài 1 — Network namespace và veth

> **Sau bài này bạn sẽ:**
> - Giải thích network namespace là "một máy mạng riêng" trong cùng kernel.
> - Dùng veth pair làm "dây mạng ảo" nối hai namespace.
> - Luôn chạy lệnh chẩn đoán **trong đúng namespace**.
>
> **Cần trước:** [N01](../../domain01-EncapsulationEthernet/README.md)–[N03](../../domain03-CIDRSubnetting/README.md). Liên hệ [L01 Execution model](../../../linux/domain1-Execution%20model/docs/README.md): namespace là thuộc tính của process.

---

## 1. Hình dung

| Đời thực | Linux |
|---|---|
| Một chiếc máy tính có card mạng, bảng route, firewall riêng | **Network namespace** |
| Sợi cáp mạng có hai đầu | **veth pair** |
| Switch | **Linux bridge** (Bài 2) |

Nhờ vậy, trên **một VM** bạn mô phỏng được nhiều "máy" và quan sát từng route table riêng — công cụ lab mạnh nhất của khóa này.

## 2. Namespace chứa những gì

Mỗi network namespace có **bản riêng** của:

```text
┌──────── namespace n04-a ────────┐   ┌──────── host (default) ─────────┐
│ interfaces (lo, veth...)        │   │ interfaces (lo, ens33...)       │
│ addresses                       │   │ addresses                       │
│ route table                     │   │ route table                     │
│ neighbor table (ARP)            │   │ neighbor table                  │
│ sockets / port space            │   │ sockets / port space            │
│ firewall rules (nftables)       │   │ firewall rules                  │
│ lo riêng (127.0.0.1 riêng!)     │   │ lo riêng                        │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

Process chạy trong namespace nào thì thấy network stack của namespace đó. Hệ quả: process ở A **không** thấy listener `127.0.0.1:8080` của B — loopback cũng là riêng.

> Namespace mới tạo **không có dây nào** và `lo` đang `DOWN`. Phải tự nối (veth, bridge...) và bật `lo`.

## 3. veth pair — dây mạng ảo

Frame đưa vào một đầu sẽ xuất hiện ở đầu kia. Đưa một đầu vào namespace khác → có dây nối hai network stack.

```text
host namespace                     n04-a namespace
 n04-a-h  ◄════════ veth ════════►  n04-a-e
```

```bash
sudo ip netns add n04-a                                   # tạo namespace
sudo ip link add n04-a-h type veth peer name n04-a-e      # tạo cặp dây
sudo ip link set n04-a-e netns n04-a                      # đẩy 1 đầu vào namespace
sudo ip netns exec n04-a ip -br link                      # nhìn từ bên trong
```

Quy tắc:

- **Cả hai đầu** phải `UP` mới chuyển frame.
- Gán IP ở đâu tùy topology. Nếu đầu host làm **port của bridge** (L2), thường **không** gán IP cho port đó — gán IP ở đầu trong namespace; bridge chỉ đóng vai switch.

## 4. Chạy lệnh trong namespace — hai cách

| Cách | Ví dụ | Dùng khi |
|---|---|---|
| `ip -n NAME ...` | `ip -n n04-a route` | Lệnh `ip` |
| `ip netns exec NAME CMD` | `ip netns exec n04-a ss -lntp` | Mọi chương trình khác (`ping`, `ss`, `curl`, `tcpdump`) |

### Lỗi kinh điển: chạy nhầm namespace

| Bạn chạy | Bạn thấy | Thật ra cần |
|---|---|---|
| `ip route get 10.64.1.12` | Route của **host** | `ip -n n04-a route get 10.64.1.12` |
| `ss -lntp` | Socket của **host** | `ip netns exec n04-a ss -lntp` |
| `tcpdump -i n04-a-e` | `No such device` | `ip netns exec n04-a tcpdump -i n04-a-e` |

> Khi ghi evidence, **luôn ghi namespace** cùng lệnh.

## 5. Cleanup an toàn

```bash
ip netns list
sudo ip netns pids n04-a     # còn process nào giữ namespace?
sudo ip netns del n04-a      # veth bên trong tự biến mất theo
```

Xóa named namespace không giải phóng ngay nếu còn process giữ nó — dừng process lab trước.

---

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Tạo namespace là có mạng." | Cần veth/bridge và bật `lo`, interface. |
| "`127.0.0.1` chung cho cả máy." | Mỗi namespace có loopback riêng. |
| "Cứ gán IP cho mọi đầu veth." | Đầu làm bridge port thường không cần IP. |

## Tự kiểm tra

1. Bạn chạy `ss -lntp` trên host và không thấy server đang chạy trong `n04-a`. Server có chết không?
2. Sau khi `ip netns add`, ping `127.0.0.1` trong namespace fail. Vì sao?
3. Xóa namespace thì veth bên trong ra sao?

<details>
<summary>Đáp án</summary>

1. Không chắc — bạn đang nhìn socket của host. Chạy `ip netns exec n04-a ss -lntp`.
2. `lo` chưa bật: `ip -n NAME link set lo up`.
3. Bị xóa cùng namespace (và đầu peer cũng biến mất).

</details>

## Nguồn

- [ip-netns(8)](https://man7.org/linux/man-pages/man8/ip-netns.8.html)
- [ip-link(8)](https://man7.org/linux/man-pages/man8/ip-link.8.html)
- [network_namespaces(7)](https://man7.org/linux/man-pages/man7/network_namespaces.7.html)
