# L09 Lab — Baseline rồi phân loại CPU / memory / I/O

| | |
|---|---|
| **Thời lượng** | 90 phút |
| **Môi trường** | VM lab; `sysstat` (`iostat`, `pidstat`, `sar`) nếu cài được. Mọi workload chạy qua `systemd-run` **có giới hạn** để không làm treo VM |
| **Mục tiêu** | Lấy baseline, tạo 3 loại tải, phân loại đúng bằng ≥ 2 bằng chứng mỗi loại, chứng minh trở về baseline |

## Phần 1 — Baseline (20 phút)

Với **mỗi lệnh**: ghi câu hỏi nó trả lời → dự đoán → kết quả.

```bash
date -u +%FT%TZ; nproc; uptime
free -h
vmstat 1 5
ps -eo pid,user,stat,%cpu,rss,comm --sort=-%cpu | head
df -h; df -i
iostat -xz 1 5          # nếu có sysstat
```

| Chỉ số | Baseline | Câu hỏi nó trả lời |
|---|---|---|
| load 1/5/15 vs `nproc` | | |
| `vmstat` r / b / si / so / wa | | |
| `free` available | | |
| `iostat` await / aqu-sz | | |

## Phần 2 — Ba loại tải (mỗi loại 10–15 phút)

Chạy từng cái, **dự đoán trước** chỉ số nào sẽ đổi, đo, rồi dừng và đo lại.

### A. CPU

```bash
systemd-run --user --unit=l09-cpu -p CPUQuota=150% \
  bash -c 'for i in $(seq $(nproc)); do (while :; do :; done) & done; wait'
vmstat 1 5; pidstat -u 1 3 2>/dev/null || top -b -n1 | head -15
systemctl --user stop l09-cpu
```

Kỳ vọng: `us` tăng, `r` tăng; `pidstat` chỉ ra bash. `CPUQuota=150%` giới hạn tổng ~1.5 CPU — kiểm bằng `systemd-cgtop`.

### B. Memory (có giới hạn)

```bash
systemd-run --user --unit=l09-mem -p MemoryMax=300M -p MemorySwapMax=0 \
  python3 -c 'import time; b=[]; [b.append(bytearray(10*1024*1024)) or time.sleep(0.2) for _ in range(100)]'
sleep 8; systemctl --user status l09-mem --no-pager | head -8
journalctl --user -u l09-mem --no-pager | tail -5
journalctl -k --since "-2 min" | grep -i oom
```

Kỳ vọng: process bị OOM-kill **trong cgroup** khi vượt 300M (`status=9/KILL` hoặc `oom-kill`); host không bị ảnh hưởng.

### C. Disk I/O

```bash
systemd-run --user --unit=l09-io -p IOWeight=10 \
  bash -c 'while :; do dd if=/dev/zero of=$HOME/l09-io.bin bs=1M count=512 oflag=direct status=none; done'
vmstat 1 5; iostat -xz 1 3 2>/dev/null; pidstat -d 1 3 2>/dev/null
systemctl --user stop l09-io; rm -f ~/l09-io.bin
```

Kỳ vọng: `b`/`wa` tăng, `w_await`/`aqu-sz` tăng; `pidstat -d` chỉ ra `dd`.

> Kiểm dung lượng trống trước (`df -h ~`) — cần ≥ 1 GiB.

## Phần 3 — Bài mù (nhờ người khác hoặc tự chọn ngẫu nhiên)

Chạy **một** trong A/B/C mà không nhìn tên unit. Phân loại chỉ bằng evidence, ghi bảng:

| Thời điểm | Bằng chứng host | Bằng chứng process | Log | Kết luận | Đúng? |
|---|---|---|---|---|---|

---

## Definition of Done

- [ ] Bảng baseline với câu hỏi cho từng chỉ số.
- [ ] A/B/C: dự đoán + ≥ 2 bằng chứng + before/after.
- [ ] B có bằng chứng OOM trong cgroup.
- [ ] Bài mù phân loại đúng.
- [ ] Giải thích vì sao `CPUQuota`/`MemoryMax` chỉ **giới hạn**, không sửa nguyên nhân.

## Cleanup

```bash
systemctl --user stop l09-cpu l09-mem l09-io 2>/dev/null
systemctl --user reset-failed
rm -f ~/l09-io.bin
```
