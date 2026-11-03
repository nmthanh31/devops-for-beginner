# Bài 5 — Hostname và DNS client

## Mục tiêu và tiền đề

Các bài trước dùng IP trực tiếp. Bài này giải thích cách application biến tên thành IP trước khi tạo connection.

Đọc lại luồng tổng quát tại [Bài 1](./01-host-network-flow.md) nếu cần.

## 1. Hostname, domain và FQDN

**Hostname** là tên local của host, ví dụ `k8s-wk`. Nó dùng trong prompt, log và nhận diện hệ thống.

**Domain name** là tên trong hệ thống phân cấp DNS, ví dụ `example.com`.

**FQDN** là tên đầy đủ xác định vị trí trong DNS hierarchy, ví dụ:

```text
api.lab.example.com
```

Máy tự đặt hostname `k8s-wk` không tự động tạo DNS record để máy Windows phân giải tên đó.

## 2. Name resolution và DNS

**Name resolution** là quá trình biến tên thành địa chỉ. Linux có thể dùng nhiều nguồn; DNS chỉ là một nguồn.

**DNS** là hệ thống tên phân tán lưu các record. Các thành phần:

- **stub resolver:** phần local nhận yêu cầu từ application;
- **recursive resolver:** DNS server tìm câu trả lời thay client và cache kết quả;
- **authoritative server:** giữ dữ liệu chính thức cho một zone;
- **zone:** phần DNS namespace do một nhóm authoritative server quản lý.

## 3. DNS record, TTL và cache

Các record thường gặp:

- `A`: tên → IPv4;
- `AAAA`: tên → IPv6;
- `CNAME`: alias → canonical name;
- `PTR`: reverse mapping IP → tên;
- `MX`: mail exchanger;
- `NS`: authoritative nameserver của zone.

**TTL** cho biết cache có thể giữ record bao lâu trước khi cần hỏi lại. Vì cache, thay đổi DNS không nhất thiết xuất hiện đồng thời ở mọi client.

## 4. NSS và thứ tự phân giải

**NSS — Name Service Switch** quyết định nguồn tra cứu cho hostname và dữ liệu hệ thống khác.

```text
/etc/nsswitch.conf
```

Ví dụ:

```text
hosts: files dns
```

Nghĩa là thử `/etc/hosts` trước, sau đó DNS. Trên hệ thống dùng systemd-resolved có thể xuất hiện module `resolve` hoặc `myhostname`.

## 5. `/etc/hosts`

Đây là bảng mapping tĩnh trên local host:

```text
192.168.220.133 k8s-wk.lab k8s-wk
```

Đặc điểm:

- chỉ ảnh hưởng máy có file đó;
- không có TTL;
- không tự đồng bộ;
- phù hợp mapping nhỏ/local/tạm thời.

Muốn Windows dùng cùng tên, Windows cũng cần DNS phù hợp hoặc hosts entry riêng.

## 6. `/etc/resolv.conf` và nameserver

`/etc/resolv.conf` mô tả resolver configuration truyền thống:

- `nameserver`: IP của DNS resolver;
- `search`: suffix được thử với tên chưa đầy đủ;
- `options`: tùy chọn resolver.

Trên Ubuntu dùng systemd-resolved, file này thường là symlink tới file được sinh tự động. Không nên sửa trực tiếp rồi kỳ vọng thay đổi tồn tại lâu dài.

```bash
ls -l /etc/resolv.conf
cat /etc/resolv.conf
```

## 7. systemd-resolved

systemd-resolved là dịch vụ local cung cấp name resolution, cache và DNS theo từng network link. Local stub thường xuất hiện ở `127.0.0.53`; đó không nhất thiết là DNS server cuối cùng.

```bash
resolvectl status
resolvectl query example.com
```

`resolvectl status` cho biết DNS server và search domain gắn với từng interface.

## 8. Luồng query

```text
application gọi getaddrinfo()
   ↓
NSS chọn nguồn
   ├── /etc/hosts
   └── resolver/systemd-resolved
             ↓
       recursive DNS resolver
             ↓ nếu cache miss
       authoritative DNS
             ↓
       record + TTL trả về application
```

Sau khi application nhận IP, DNS kết thúc nhiệm vụ. Route, TCP và application protocol diễn ra tiếp.

## 9. `getent`, `dig`, `host` khác nhau thế nào?

```bash
getent ahosts example.com
dig example.com
dig @1.1.1.1 example.com
host example.com
```

| Công cụ | Câu hỏi |
|---|---|
| `getent ahosts` | Application qua NSS sẽ nhận địa chỉ nào? |
| `dig NAME` | DNS mặc định trả lời gì? |
| `dig @SERVER NAME` | DNS server cụ thể trả lời gì? |
| `host NAME` | DNS lookup cơ bản dạng gọn |

Nếu `dig` thành công nhưng `getent` thất bại, điều tra NSS/local resolver. Nếu kết nối bằng IP được nhưng tên thất bại, ưu tiên DNS/name resolution.

## 10. Nhận diện lỗi

```text
Could not resolve host
Temporary failure in name resolution
Name or service not known
```

Đây là lỗi giai đoạn name resolution. Chúng khác với:

```text
Connection refused
Connection timed out
Network is unreachable
```

Những lỗi sau xảy ra khi hệ thống đã có hoặc đang xử lý destination IP/connection.

<!-- learn:tail -->
## Tự kiểm tra

1. `/etc/resolv.conf` chỉ có `nameserver 127.0.0.53`. DNS server thật xem ở đâu?
2. `dig app.lab` trả IP A, `getent hosts app.lab` trả IP B. Nghi gì?

<details>
<summary>Đáp án</summary>

1. `resolvectl status` (systemd-resolved là stub local).
2. `/etc/hosts` có mapping khác và `nsswitch.conf` đặt `files` trước `dns`.

</details>

## Nguồn

- [LPIC-1 V5.0 — Objectives 109.2 và 109.4](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

