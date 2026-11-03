# L10 Lab — Chứng minh luồng Windows → VM

| | |
|---|---|
| **Thời lượng** | 75 phút |
| **Môi trường** | Windows host + VM lab trên VMware. Chỉ đổi **service lab** của bạn; không đổi route/Netplan của interface SSH |
| **Mục tiêu** | Chứng minh từng lớp Windows NIC → VMware network → VM NIC → route → firewall → socket → process; tái hiện refused, timeout, 404 |

## Bước 1 — Baseline trên VM

```bash
ip -br link
ip -br addr
ip route
ip route get <IP-Windows>
sudo ss -lntp
resolvectl status | head -20
```

| Mục | Giá trị |
|---|---|
| VM NIC / IP / prefix | |
| Gateway | |
| Route về Windows (dev, src) | |
| DNS server | |

## Bước 2 — Service lab, hai kiểu bind

```bash
mkdir -p ~/l10/www && echo ok > ~/l10/www/healthz && cd ~/l10/www
python3 -m http.server 18010 --bind 127.0.0.1 &      # A: loopback
```

**Dự đoán** trước khi chạy:

| Test | Từ | Kết quả dự đoán | Thực tế |
|---|---|---|---|
| `curl 127.0.0.1:18010/healthz` | VM | | |
| `curl <VM-IP>:18010/healthz` | VM | | |
| `Test-NetConnection <VM-IP> -Port 18010` | Windows | | |
| `curl.exe http://<VM-IP>:18010/healthz` | Windows | | |

Rồi đổi bind:

```bash
kill %1; python3 -m http.server 18010 --bind 0.0.0.0 &     # B: mọi IPv4
sudo ss -lntp 'sport = :18010'
```

Lặp lại 4 test.

## Bước 3 — Tái hiện 3 triệu chứng

| Triệu chứng | Cách tạo (chỉ trên service lab) | Bằng chứng lớp |
|---|---|---|
| `refused` | Dừng server (`kill %1`) | `ss` không có listener; capture `[S]` → `[R.]` |
| `timeout` | Chỉ khi có console: `sudo ufw deny 18010/tcp` (UFW đang active) **hoặc** gọi tới IP không tồn tại cùng subnet | Capture: SYN tới, không trả lời |
| `404` | Server chạy, gọi `/khong-co` | HTTP response 404 từ đúng process |

Capture trên VM khi test từ Windows:

```bash
sudo tcpdump -ni <VM-NIC> 'tcp port 18010'
```

Rollback mọi thay đổi firewall (`sudo ufw delete deny 18010/tcp`).

## Bước 4 — Viết đường đi

Vẽ: Windows NIC → VMware vSwitch/NAT → VM NIC → IP dst → firewall → socket `0.0.0.0:18010` → process `python3`. Với mỗi mũi tên ghi **một lệnh** chứng minh.

---

## Definition of Done

- [ ] Bảng baseline + bảng dự đoán/thực tế cho bind loopback vs 0.0.0.0.
- [ ] 3 triệu chứng, mỗi cái có 2 lớp evidence (client message + `ss`/capture).
- [ ] Sơ đồ đường đi có lệnh chứng minh từng chặng.
- [ ] Không đổi route/Netplan/interface SSH; firewall đã rollback.

## Cleanup

```bash
kill %1 2>/dev/null; pkill -f 'http.server 18010'; rm -r ~/l10
```
