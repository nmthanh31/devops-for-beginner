# N11 Bài 1 — OSPF học route như thế nào?

> **Sau bài này bạn sẽ:**
> - Phân biệt static route, OSPF (link state), BGP (policy) ở mức nhận diện.
> - Theo chuỗi **neighbor → LSDB → SPF → route trong FRR → route trong kernel → packet**.
> - Biết trạng thái neighbor kẹt ở đâu thì nghi gì.
>
> **Cần trước:** [N05](../../domain05-RoutingReturnPath/README.md).

---

## 1. Hình dung: bản đồ chung

- **Static route** = mỗi tài xế tự ghi chỉ đường trên giấy. Đường xa bị sập, giấy không tự sửa.
- **OSPF** = các trạm điều phối **chia sẻ bản đồ** (LSA) cho nhau; ai cũng có bản đồ giống nhau (LSDB) rồi tự tính đường ngắn nhất (SPF). Một đường sập → báo cho mọi trạm → tính lại.
- **BGP** = các công ty vận tải thỏa thuận "tôi cho anh đi qua vùng tôi theo điều kiện X" — trao đổi reachability + **policy** giữa tổ chức. (Chỉ nhận diện, chưa cấu hình.)

> OSPF **không chuyển packet**. Daemon tính route rồi cài vào kernel; **kernel/FIB** mới forward data packet.

## 2. Chuỗi hoạt động

```text
① Hello          phát hiện neighbor, duy trì quan hệ
② Adjacency      đồng bộ LSDB (trạng thái tới Full)
③ LSA flood      mô tả link/prefix trong area
④ LSDB           cơ sở dữ liệu topology
⑤ SPF            tính đường ngắn nhất
⑥ Route (FRR)    zebra chọn route
⑦ Kernel FIB     ip route — đây mới là thứ forward packet
```

### Trạng thái neighbor

```text
Down → Init → 2-Way → ExStart → Exchange → Loading → Full
```

| Kẹt ở | Nghi |
|---|---|
| Không thấy neighbor | Link/IP/VLAN, firewall chặn proto 89 / multicast 224.0.0.5 |
| `Init` | Hello chỉ đi một chiều |
| `2-Way` (trên broadcast) | Bình thường giữa hai DROther — không phải lỗi |
| `ExStart` / `Exchange` | **MTU mismatch** |
| Không lên do tham số | Area ID, hello/dead timer, network type, authentication khác nhau |
| `Full` nhưng thiếu route | Prefix chưa được quảng bá, area, route selection |

## 3. Quy trình debug

| # | Lệnh | Câu hỏi |
|---|---|---|
| 1 | `ping` IP router kia | Link/IP thấy nhau? |
| 2 | `tcpdump -ni IF proto ospf` | Hello gửi/nhận cả hai chiều? |
| 3 | `vtysh -c 'show ip ospf neighbor'` | Trạng thái? |
| 4 | `vtysh -c 'show ip ospf database'` | LSA của mạng cần đi có không? |
| 5 | `vtysh -c 'show ip route ospf'` | FRR chọn route? |
| 6 | `ip route get DEST` | **Kernel** dùng route nào? (có thể route khác ưu tiên hơn) |
| 7 | ping/capture data | Packet thật đi/về? |

**FRR** là routing suite chạy trên Linux; `vtysh` là CLI. **Area 0** là backbone trong thiết kế nhiều area.

> Route học được ở R1 **chưa** chứng minh return route ở R2.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Neighbor Full = traffic chạy." | Còn route trong kernel, return path, firewall. |
| "OSPF forward packet." | Kernel forward; OSPF chỉ tính route. |
| "Kẹt ExStart là lỗi password." | Hay gặp nhất là MTU mismatch. |

## Tự kiểm tra

1. FRR có `show ip route ospf` chứa `10.11.2.0/24`, nhưng `ip route get 10.11.2.10` đi qua default. Vì sao có thể?
2. Hai router kẹt `ExStart`. Kiểm gì trước?

<details>
<summary>Đáp án</summary>

1. Route chưa được zebra cài vào kernel (hoặc có route khác ưu tiên hơn / admin distance / sai VRF). So `show ip route` với `ip route`.
2. MTU hai đầu interface.

</details>

## Nguồn

[FRR OSPFv2](https://docs.frrouting.org/en/latest/ospfd.html) · [RFC 2328 OSPFv2](https://www.rfc-editor.org/rfc/rfc2328)
