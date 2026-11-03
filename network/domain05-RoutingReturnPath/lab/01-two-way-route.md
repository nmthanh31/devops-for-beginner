# N05 Lab — Một chiều đúng, chiều về sai

| | |
|---|---|
| **Thời lượng** | 75 phút |
| **Môi trường** | VM lab, 3 namespace cô lập |
| **Mục tiêu** | Tái hiện thiếu return route, định vị bằng paired capture, sửa tối thiểu |

```text
n05-c 10.51.1.10/24 ── c-e ═══ r-c ── [n05-r] ── r-s ═══ s-e ── n05-s 10.52.1.20/24
                              10.51.1.1        10.52.1.1
```

## Bước 0 — Dựng topology

```bash
ip netns list | grep n05 && echo "ĐÃ TỒN TẠI — dừng lại kiểm tra"
for ns in n05-c n05-r n05-s; do sudo ip netns add $ns; sudo ip -n $ns link set lo up; done
sudo ip link add c-e netns n05-c type veth peer name r-c netns n05-r
sudo ip link add s-e netns n05-s type veth peer name r-s netns n05-r
sudo ip -n n05-c addr add 10.51.1.10/24 dev c-e
sudo ip -n n05-r addr add 10.51.1.1/24  dev r-c
sudo ip -n n05-r addr add 10.52.1.1/24  dev r-s
sudo ip -n n05-s addr add 10.52.1.20/24 dev s-e
for p in "n05-c c-e" "n05-r r-c" "n05-r r-s" "n05-s s-e"; do set -- $p; sudo ip -n $1 link set $2 up; done
sudo ip netns exec n05-r sysctl -qw net.ipv4.ip_forward=1
sudo ip -n n05-c route add 10.52.1.0/24 via 10.51.1.1
# CỐ Ý chưa thêm route về trên server
```

## Bước 1 — Dự đoán

| Câu hỏi | Dự đoán |
|---|---|
| `ping 10.52.1.20` từ client kết quả? | |
| Server có nhận Echo Request? | |
| Server có gửi Echo Reply? Vì sao? | |
| `ip -n n05-s route get 10.51.1.10` ra gì? | |

## Bước 2 — Paired capture

Mở 2 terminal capture:

```bash
sudo ip netns exec n05-r tcpdump -ni r-c icmp    # phía client của router
sudo ip netns exec n05-s tcpdump -ni s-e icmp    # tại server
```

Terminal 3:

```bash
sudo ip netns exec n05-c ping -c 3 -W 1 10.52.1.20
sudo ip -n n05-c route get 10.52.1.20
sudo ip -n n05-s route get 10.51.1.10
```

**Kết quả mong đợi:** server thấy Echo Request, **không** gửi reply; `route get` trên server báo `Network is unreachable` (không có route nào). Router `r-c` chỉ thấy request.

> Khác với ví dụ (server có default sai → reply đi lạc), ở đây server **không có route** → kernel không gửi reply được. Cả hai đều là lỗi return path.

## Bước 3 — Sửa và verify

```bash
sudo ip -n n05-s route add 10.51.1.0/24 via 10.52.1.1
sudo ip netns exec n05-c ping -c 2 10.52.1.20
```

Thêm phép thử TCP:

```bash
sudo ip netns exec n05-s python3 -m http.server 8080 --bind 10.52.1.20 &
sudo ip netns exec n05-c curl -s -o /dev/null -w '%{http_code}\n' http://10.52.1.20:8080/
```

## Bước 4 — Negative test

```bash
sudo ip -n n05-s route del 10.51.1.0/24
sudo ip netns exec n05-c curl -m 3 http://10.52.1.20:8080/   # timeout
sudo ip -n n05-s route add 10.51.1.0/24 via 10.52.1.1        # restore
```

Thêm một biến thể: tắt forwarding ở router (`sysctl -w net.ipv4.ip_forward=0` trong `n05-r`), dự đoán capture nào còn thấy packet, rồi bật lại.

---

## Definition of Done

- [ ] Sơ đồ IP + route table cả 3 namespace.
- [ ] Dự đoán viết trước.
- [ ] Paired capture chứng minh request tới server, reply không về.
- [ ] `route get` hai đầu làm lớp evidence thứ hai.
- [ ] Sửa bằng **một** route trên server; positive (ping + HTTP) và negative test.

## Cleanup

```bash
sudo pkill -f 'http.server 8080'
for ns in n05-c n05-r n05-s; do sudo ip netns pids $ns; done   # phải rỗng
for ns in n05-c n05-r n05-s; do sudo ip netns del $ns; done
ip netns list
```
