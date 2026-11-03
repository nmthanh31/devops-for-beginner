# N03 Lab — Tự chia mạng và kiểm bằng kernel

| | |
|---|---|
| **Thời lượng** | 60 phút |
| **Môi trường** | Giấy/bút cho phần 1; VM lab cho phần 3 |
| **Mục tiêu** | Tính tay chính xác, rồi để **kernel** xác nhận dự đoán on-link/gateway |

---

## Phần 1 — Tính tay (15 phút, không calculator)

| IP/prefix | Network | Broadcast | Host range | Số host |
|---|---|---|---|---|
| `10.33.8.77/27` | | | | |
| `172.18.9.200/26` | | | | |
| `192.168.220.133/24` | | | | |
| `10.0.0.5/30` | | | | |

## Phần 2 — Dự đoán on-link hay gateway

Source là `192.168.220.133/26`. Với mỗi đích, host gửi **trực tiếp** hay **qua gateway**?

| Đích | Dự đoán | Lý do (block nào?) |
|---|---|---|
| `192.168.220.1` | | |
| `192.168.220.65` | | |
| `192.168.220.130` | | |
| `192.168.220.190` | | |

## Phần 3 — Để kernel xác nhận

```bash
sudo ip netns add n03
sudo ip -n n03 link add n03-d type dummy
sudo ip -n n03 addr add 192.168.220.133/26 dev n03-d
sudo ip -n n03 link set n03-d up
sudo ip -n n03 route add default via 192.168.220.129

for d in 192.168.220.1 192.168.220.65 192.168.220.130 192.168.220.190; do
  sudo ip -n n03 route get $d
done
```

> `dummy` là interface ảo không nối đâu cả — đủ để kernel tính route mà không gửi gì ra mạng thật.

**Kết quả mong đợi:** đích nào có `via 192.168.220.129` là qua gateway; không có `via` là on-link. Đối chiếu với phần 2, đánh dấu chỗ sai và tìm bit nhầm.

Kiểm phần 1 bằng công cụ:

```bash
python3 -c "import ipaddress as i
for s in ['10.33.8.77/27','172.18.9.200/26','192.168.220.133/24','10.0.0.5/30']:
    n=i.ip_interface(s).network; print(s, n.network_address, n.broadcast_address, n.num_addresses)"
```

## Phần 4 — Thiết kế

Thiết kế **hai subnet không overlap** cho client/server lab, mỗi subnet **≥ 20 host usable**, prefix nhỏ nhất có thể. Không được trùng route hiện có trên VM (`ip route`).

| Segment | Prefix | Gateway | Host range | Vì sao chọn prefix này |
|---|---|---|---|---|
| Client | | | | |
| Server | | | | |

<details>
<summary>Gợi ý</summary>

≥ 20 host → cần ≥ 22 địa chỉ → `/27` (30 host) là nhỏ nhất. Ví dụ `10.63.1.0/27` và `10.63.1.32/27`.

</details>

---

## Definition of Done

- [ ] Phần 1 tính tay xong trước khi dùng công cụ, ghi rõ chỗ sai.
- [ ] Phần 2 dự đoán trước, phần 3 có output `route get` xác nhận.
- [ ] Phần 4: hai prefix không overlap với nhau **và** với `ip route` của VM; giải thích chọn prefix.

## Cleanup

```bash
sudo ip netns del n03
ip netns list
```
