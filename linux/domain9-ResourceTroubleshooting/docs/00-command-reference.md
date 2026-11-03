# L09 — Command reference

## Baseline nhanh

```bash
date --iso-8601=seconds
hostname
uptime
nproc
free -h
vmstat 1 5
```

| Lệnh | Trả lời câu hỏi |
|---|---|
| `uptime` | Load 1/5/15 phút và thời gian máy đã chạy |
| `nproc` | Có bao nhiêu processing unit khả dụng |
| `free -h` | Memory available, cache và swap |
| `vmstat 1 5` | Run queue, blocked task, swap, I/O và CPU theo năm mẫu |

## CPU và process

```bash
top
top -H -p PID
ps -eo pid,ppid,user,stat,ni,pri,%cpu,%mem,comm,args --sort=-%cpu
pstree -p
pidstat 1
```

| Argument | Ý nghĩa |
|---|---|
| `top -H` | Hiện thread |
| `top -p PID` | Chỉ theo dõi PID đã chọn |
| `ps -e` | Chọn mọi process |
| `ps -o ...` | Chọn các cột output |
| `--sort=-%cpu` | Sắp xếp CPU giảm dần |
| `pstree -p` | Hiện PID trong cây process |
| `pidstat 1` | Lấy mẫu theo process mỗi giây |

## Memory

```bash
free -h
ps -eo pid,ppid,user,%mem,rss,vsz,stat,comm,args --sort=-rss
vmstat 1 10
sudo journalctl -k -g 'oom|out of memory|killed process' --no-pager
```

| Trường | Ý nghĩa |
|---|---|
| `available` | RAM ước lượng có thể cấp thêm mà chưa cần swap mạnh |
| `RSS` | Memory vật lý đang cư trú |
| `VSZ` | Không gian địa chỉ ảo |
| `si`, `so` | Swap in và swap out |

## Disk và I/O

```bash
df -h
df -i
lsblk -f
findmnt
iostat -xz 1 10
sudo iotop -oPa
pidstat -d 1
sudo lsof -p PID
```

| Argument | Ý nghĩa |
|---|---|
| `df -h` | Dung lượng theo đơn vị dễ đọc |
| `df -i` | Mức sử dụng inode |
| `iostat -x` | Thống kê thiết bị mở rộng |
| `iostat -z` | Ẩn thiết bị không hoạt động |
| `iotop -o` | Chỉ hiện task có I/O |
| `iotop -P` | Gộp theo process |
| `iotop -a` | Hiện I/O tích lũy |
| `pidstat -d` | I/O theo process |
| `lsof -p PID` | File/device process đang mở |

## Dữ liệu lịch sử

```bash
sar -u
sar -r
sar -q
sar -d
```

`sar` cần việc thu thập dữ liệu của `sysstat` đã được cài và bật từ trước.

## Systemd và cgroup

```bash
systemd-cgls
systemd-cgtop
systemctl status UNIT
systemctl show UNIT
```

## Thứ tự chẩn đoán gợi ý

```text
uptime/free/vmstat
        ↓
CPU?    → top/ps/pidstat
memory? → free/ps/vmstat/kernel journal
I/O?    → iostat/iotop/pidstat/lsof
        ↓
đối chiếu service log và timeline
```

## Cảnh báo

- Không kill process chỉ vì nó đứng đầu `top`.
- Không drop cache hoặc tắt swap để “thử” trên hệ thống đang dùng thật.
- Không đổi nice/cgroup limit trước khi ghi baseline và có phương án rollback.
- Không kết luận từ một mẫu duy nhất.

## Nguồn

- [LPIC-2 V4.5 — Objective 200.1](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
- [LPIC-2 V5.0 draft — Objective 204.3](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V5.0)
