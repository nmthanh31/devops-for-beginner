# Bài 6 — Cấu hình mạng bền vững

## Mục tiêu và tiền đề

Các bài trước quan sát trạng thái kernel. Bài này giải thích hệ thống nào tạo lại interface address, route và DNS sau reboot.

## 1. Runtime và persistent configuration

**Runtime state** là trạng thái kernel đang dùng ngay lúc này:

- interface up/down;
- IP/prefix;
- route;
- neighbor;
- socket.

Lệnh `ip addr add` hoặc `ip route add` thay đổi runtime trực tiếp.

**Persistent configuration** là cấu hình được lưu để network daemon tái tạo address, route và DNS sau boot/reconnect.

```text
persistent config
      ↓
network manager/daemon
      ↓
kernel runtime state
      ↓
packet được gửi nhận
```

## 2. Daemon, device và connection profile

**Daemon** là process nền quản lý một chức năng hệ thống.

**NetworkManager** là network management daemon. Trong NetworkManager:

- **device:** interface kernel như `ens33`;
- **connection profile:** cấu hình có tên chứa address, route, DNS và phương thức IPv4/IPv6.

```bash
nmcli device status
nmcli connection show
nmcli connection show CONNECTION_NAME
```

Một profile có thể được activate trên device. Device và profile không phải cùng một đối tượng.

## 3. systemd-networkd

systemd-networkd là daemon đọc network unit rồi áp dụng link/address/route vào kernel.

Network unit thường nằm trong `/etc/systemd/network/` và có thể dùng file `.network`, `.netdev`, `.link` cho các mục đích khác nhau.

```bash
networkctl list
networkctl status INTERFACE
```

Không nên để hai manager cùng tranh quyền cấu hình một interface nếu chưa có thiết kế rõ.

## 4. Netplan trên Ubuntu

Netplan là lớp cấu hình YAML. Nó đọc:

```text
/etc/netplan/*.yaml
```

rồi sinh cấu hình cho **renderer/backend**:

- NetworkManager; hoặc
- systemd-networkd.

```text
Netplan YAML
   ↓ generate
renderer configuration
   ↓ daemon applies
kernel interface/address/route
```

YAML phụ thuộc indentation; sai thụt lề có thể làm config lỗi hoặc đổi ý nghĩa.

## 5. DHCP và lease

DHCP cấp cấu hình động. Với DHCPv4, luồng cơ bản DORA:

```text
client                         server
   | ---- Discover ----------> |
   | <--- Offer -------------- |
   | ---- Request -----------> |
   | <--- Acknowledge -------- |
```

DHCP có thể cấp:

- IP/prefix;
- default gateway;
- DNS/search domain;
- lease time;
- option khác.

**Lease** là quyền sử dụng cấu hình trong một khoảng thời gian. Client renew trước khi lease hết hạn.

## 6. Ví dụ Netplan DHCP

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      dhcp4: true
```

Phải dùng đúng interface thực tế của máy.

## 7. Ví dụ Netplan static

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      addresses:
        - 192.0.2.10/24
      routes:
        - to: default
          via: 192.0.2.1
      nameservers:
        addresses:
          - 192.0.2.53
```

`192.0.2.0/24` là dải tài liệu. Không copy trực tiếp vào VM; phải thay bằng IP, prefix, gateway và DNS đúng của mạng thật.

## 8. Source of truth

**Source of truth** là nơi cấu hình gốc cần chỉnh. Trên Ubuntu dùng Netplan, thường là `/etc/netplan/*.yaml`.

Không chỉnh generated backend file rồi kỳ vọng thay đổi tồn tại sau lần `netplan generate/apply` tiếp theo.

Kiểm tra trước khi sửa:

```bash
ls -l /etc/netplan
sudo netplan get
systemctl is-active NetworkManager
systemctl is-active systemd-networkd
```

## 9. Generate, apply và try

- `netplan generate`: kiểm tra YAML và sinh backend config;
- `netplan apply`: áp dụng cấu hình;
- `netplan try`: áp dụng thử, yêu cầu xác nhận và rollback theo timeout.

Đổi network qua SSH có thể tự cắt kết nối. Cần console VM hoặc phương án recovery.

Quy trình:

```text
ghi baseline
→ backup đúng file cấu hình
→ sửa YAML
→ netplan generate
→ netplan try
→ xác nhận connectivity
→ verify runtime state
```

## 10. Verify

```bash
ip -br link
ip -br addr
ip route
ip route get DESTINATION_IP
resolvectl status
getent ahosts EXPECTED_NAME
```

Nếu mục tiêu là inbound connectivity, phải test từ client khác. Khi lab yêu cầu persistence, reboot có kiểm soát rồi kiểm tra lại.

<!-- learn:tail -->
## Tự kiểm tra

1. Vì sao dùng `netplan try` thay vì `netplan apply` khi đang SSH?
2. Sửa file Netplan nhưng `ip addr` không đổi. Thiếu bước gì?

<details>
<summary>Đáp án</summary>

1. `try` tự rollback sau timeout nếu bạn không xác nhận — tránh tự khóa khi cấu hình sai.
2. `netplan generate`/`apply` (hoặc `try`) — file chỉ là source of truth, chưa áp vào runtime.

</details>

## Nguồn

- [LPIC-1 V5.0 — Objective 109.2](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [Ubuntu Server — Configuring networks](https://ubuntu.com/server/docs/explanation/networking/configuring-networks/)
- [Netplan CLI](https://netplan.readthedocs.io/en/stable/cli/)

