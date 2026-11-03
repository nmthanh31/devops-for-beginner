# N09 Lab — Filter và NAT trong namespace

| | |
|---|---|
| **Thời lượng** | 90 phút |
| **Môi trường** | VM lab, `nft`, `tcpdump`, `python3`; `conntrack` (gói `conntrack`) nếu có |
| **Mục tiêu** | (1) forward filter stateful: port cho phép / bị chặn; drop vs reject. (2) SNAT: chứng minh tuple đổi |
| **An toàn** | Mọi `nft` chạy **trong namespace router**. **Không** `nft flush ruleset` trên host |

```text
n09-c 10.9.1.10 ── c-e═r-c 10.9.1.1 [n09-r] 10.9.2.1 r-s═s-e ── n09-s 10.9.2.20 (HTTP :80, :8080)
```

## Bước 0 — Dựng và baseline

```bash
for ns in n09-c n09-r n09-s; do sudo ip netns add $ns; sudo ip -n $ns link set lo up; done
sudo ip link add c-e netns n09-c type veth peer name r-c netns n09-r
sudo ip link add s-e netns n09-s type veth peer name r-s netns n09-r
sudo ip -n n09-c addr add 10.9.1.10/24 dev c-e
sudo ip -n n09-r addr add 10.9.1.1/24 dev r-c
sudo ip -n n09-r addr add 10.9.2.1/24 dev r-s
sudo ip -n n09-s addr add 10.9.2.20/24 dev s-e
for p in "n09-c c-e" "n09-r r-c" "n09-r r-s" "n09-s s-e"; do set -- $p; sudo ip -n $1 link set $2 up; done
sudo ip netns exec n09-r sysctl -qw net.ipv4.ip_forward=1
sudo ip -n n09-c route add default via 10.9.1.1
sudo ip -n n09-s route add default via 10.9.2.1
sudo ip netns exec n09-s python3 -m http.server 80   --bind 10.9.2.20 >/dev/null 2>&1 &
sudo ip netns exec n09-s python3 -m http.server 8080 --bind 10.9.2.20 >/dev/null 2>&1 &

C="sudo ip netns exec n09-c curl -s -m 3 -o /dev/null -w %{http_code}\n"
$C http://10.9.2.20/ ; $C http://10.9.2.20:8080/      # cả hai 200
```

## Phần 1 — Forward filter

**Dự đoán** với ruleset dưới: `:80` và `:8080` ra gì?

```bash
sudo ip netns exec n09-r nft -f - <<'EOF'
table inet n09 {
  chain fwd {
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
    iifname "r-c" tcp dport 80 counter accept
    counter
  }
}
EOF
$C http://10.9.2.20/ ; $C http://10.9.2.20:8080/
sudo ip netns exec n09-r nft list ruleset -a
```

**Kết quả mong đợi:** `:80` → `200`; `:8080` → `000` sau 3 giây (**timeout**); counter của rule cuối tăng.

**Thí nghiệm A — thiếu established:** xóa rule `ct state` (dùng handle từ `-a`):

```bash
sudo ip netns exec n09-r nft delete rule inet n09 fwd handle <HANDLE_CT>
$C http://10.9.2.20/      # giờ cũng timeout — vì sao?
sudo ip netns exec n09-r nft insert rule inet n09 fwd ct state established,related accept
```

**Thí nghiệm B — drop vs reject:** lấy handle của rule `counter` cuối từ `nft list ruleset -a`, chèn rule reject **trước** nó:

```bash
sudo ip netns exec n09-r nft insert rule inet n09 fwd position <HANDLE_COUNTER> iifname "r-c" tcp dport 8080 reject with tcp reset
time sudo ip netns exec n09-c curl -m 3 http://10.9.2.20:8080/
```

`curl :8080` giờ báo gì (refused hay timeout)? Mất bao lâu so với trước?

## Phần 2 — SNAT

```bash
sudo ip netns exec n09-r nft -f - <<'EOF'
table ip n09nat {
  chain post { type nat hook postrouting priority 100; oifname "r-s" masquerade; }
}
EOF
sudo ip netns exec n09-r tcpdump -ni r-c 'tcp port 80' &
sudo ip netns exec n09-r tcpdump -ni r-s 'tcp port 80' &
$C http://10.9.2.20/
sudo ip netns exec n09-r conntrack -L 2>/dev/null | grep dport=80
```

**Kết quả mong đợi:** `r-c` thấy source `10.9.1.10`; `r-s` thấy source **`10.9.2.1`**. Conntrack có dòng với `src=10.9.1.10 ... src=10.9.2.20 dst=10.9.2.1`.

**Chứng minh NAT thay route về:** xóa default route của server (`ip -n n09-s route del default`) → `curl` vẫn 200 (server chỉ cần trả về `10.9.2.1` on-link). Rồi xóa table `n09nat` → curl timeout. Giải thích.

---

## Definition of Done

- [ ] Bảng từng rule: hook, thứ tự, match, verdict.
- [ ] Positive/negative matrix (port × kết quả × counter).
- [ ] Thí nghiệm A giải thích được vai trò `established`.
- [ ] Thí nghiệm B: timeout vs refused + thời gian.
- [ ] SNAT: capture hai phía + conntrack (hoặc capture nếu không có tool).
- [ ] Một đoạn: vì sao đổi policy `input` của host có thể cắt SSH.

## Cleanup

```bash
sudo pkill -f 'http.server 80'; sudo pkill -f 'tcpdump -ni r-'
for ns in n09-c n09-r n09-s; do sudo ip netns del $ns; done   # table nft trong namespace biến mất cùng
ip netns list
```
