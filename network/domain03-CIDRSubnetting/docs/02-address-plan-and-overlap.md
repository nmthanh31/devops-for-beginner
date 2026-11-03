# N03 Bài 2 — Lập address plan, longest prefix match và tránh overlap

> **Sau bài này bạn sẽ:**
> - Viết address plan như một **hợp đồng** trước khi cấu hình.
> - Dự đoán route nào thắng bằng **longest prefix match**.
> - Phát hiện overlap giữa lab với VPN/VMware/cloud trước khi nó gây lỗi.
>
> **Cần trước:** [Bài 1 — CIDR](./01-cidr-calculation.md).

---

## 1. Address plan là hợp đồng

Viết **trước** khi bật bridge hay service. Mỗi dòng trả lời: segment là broadcast domain nào, ai là gateway, dải nào tĩnh, dải nào DHCP.

| Segment | Prefix | Gateway | VLAN / namespace | Dải tĩnh | Mục đích |
|---|---|---|---|---|---|
| Lab A | `10.60.1.0/24` | `10.60.1.1` | VLAN 10 | `.10–.49` | client |
| Lab B | `10.60.2.0/24` | `10.60.2.1` | VLAN 20 | `.10–.49` | server |

Và ghi **cả đường về**:

| Từ | Tới | Route cần có |
|---|---|---|
| Client `10.60.1.0/24` | Server `10.60.2.0/24` | client: via `10.60.1.1` |
| Server `10.60.2.0/24` | Client `10.60.1.0/24` | server: via `10.60.2.1` ← **hay quên** |

> Gateway `10.60.1.1` nằm ở VLAN 10 thì client ở VLAN 20 **không** dùng được nó, dù IP "trông đúng subnet". L2 phải nối được trước. Return path học kỹ ở [N05](../../domain05-RoutingReturnPath/README.md).

## 2. Longest prefix match

Khi nhiều route cùng chứa đích, kernel chọn route có **prefix dài nhất** (cụ thể nhất).

```text
Route table:
  default         via 192.168.1.1     (/0)
  10.60.0.0/16    via vpn0            (/16)
  10.60.1.0/24    dev veth-lab        (/24)

Đích 10.60.1.20  → khớp cả 3 → /24 thắng → veth-lab
Đích 10.60.5.5   → khớp /0 và /16 → /16 thắng → vpn0
Đích 8.8.8.8     → chỉ khớp /0 → default
```

Kiểm bằng dữ liệu thật, không bằng sơ đồ:

```bash
ip route get 10.60.1.20
```

## 3. Overlap — vì sao nguy hiểm

**Overlap** = hai prefix có chung địa chỉ. Ví dụ: host đã có route `10.60.0.0/16` qua VPN công ty. Bạn tạo lab `10.60.1.0/24` qua veth. Từ đó mọi packet tới `10.60.1.x` của **công ty** sẽ đi vào **lab** (vì `/24` dài hơn). Không có lỗi nào báo — chỉ là đi sai chỗ.

### Checklist trước khi chọn CIDR cho lab

```bash
ip route                 # route hiện có (VPN, Docker, VMware...)
ip -br addr              # địa chỉ trên mọi interface
docker network ls 2>/dev/null   # Docker hay dùng 172.17.0.0/16+
```

- [ ] Prefix lab không nằm trong route nào đang có.
- [ ] Không trùng dải VMware NAT/host-only, Docker, VPN, VPC cloud.

**Private IPv4** (RFC 1918): `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. "Private" không có nghĩa "không trùng" — vô số mạng dùng cùng dải, nên overlap khi nối VPN/peering là rất phổ biến.

---

## 4. Quy trình kiểm address plan

1. Tính tay network / broadcast / host range ([Bài 1](./01-cidr-calculation.md)).
2. Gắn IP trong **namespace lab**.
3. `ip route get <đích>` → on-link hay qua gateway? Đúng ý định không?
4. Test cùng subnet và khác subnet; ghi `ip neigh` làm evidence.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Route nào thêm sau thì thắng." | Prefix **dài nhất** thắng, không phụ thuộc thứ tự thêm. |
| "Dải private thì không bao giờ trùng." | Trùng rất thường khi nối VPN/cloud. |
| "Client có route tới server là đủ." | Server cũng cần route về. |

## Tự kiểm tra

Route table: `default via 192.168.1.1`, `10.0.0.0/8 via 10.255.0.1`, `10.10.0.0/16 dev lab0`, `10.10.10.0/24 via 10.10.0.254`.

1. Đích `10.10.10.5` đi đâu?
2. Đích `10.10.99.1`?
3. Đích `10.200.1.1`?
4. Đích `172.16.0.1`?

<details>
<summary>Đáp án</summary>

1. `/24` → via `10.10.0.254`.
2. `/16` → `dev lab0` (on-link).
3. `/8` → via `10.255.0.1`.
4. Chỉ khớp default → via `192.168.1.1`.

</details>

## Nguồn

- [RFC 4632 — CIDR](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 1918 — Private address space](https://www.rfc-editor.org/rfc/rfc1918)
