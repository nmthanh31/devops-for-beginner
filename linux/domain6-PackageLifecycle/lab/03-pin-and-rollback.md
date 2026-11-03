# L06-03 — Hold, rollback version và config được giữ lại

| | |
|---|---|
| **Thời lượng** | 45 phút |
| **Môi trường** | VM lab Ubuntu/Debian; package nhỏ `tree` (hoặc `jq`) |
| **Mục tiêu** | Chứng minh: (1) hold chặn upgrade; (2) rollback về version cũ khi còn tải được; (3) `remove` giữ config, `purge` xóa config |

## Bước 1 — Version có sẵn

```bash
apt-cache policy tree
apt list -a tree 2>/dev/null
ls /var/cache/apt/archives/ | grep -i tree || true
```

Ghi: version installed, candidate, các version khác trong repo. **Nếu chỉ có một version**, bước 3 chỉ làm phần mô phỏng (`-s`) và ghi chú "không có version cũ để rollback" — đây cũng là một phát hiện vận hành quan trọng.

## Bước 2 — Hold

```bash
sudo apt install -y tree
sudo apt-mark hold tree
apt-mark showhold
apt-get -s install --only-upgrade tree      # kết quả? có dòng "kept back"/"held"?
sudo apt-mark unhold tree
```

## Bước 3 — Rollback (nếu có version cũ)

```bash
OLD=<version cũ từ bước 1>
apt-get -s install tree=$OLD                 # đọc kế hoạch: Downgrade?
sudo apt install -y --allow-downgrades tree=$OLD
dpkg -s tree | grep Version
tree --version
sudo apt install -y tree                     # quay lại candidate
```

## Bước 4 — Config: remove vs purge (dùng package có conffile)

`tree` không có file cấu hình, nên dùng một package nhỏ có conffile, ví dụ `nano` với `/etc/nanorc`:

```bash
dpkg -s nano | grep -i conffiles -A3
sudo cp /etc/nanorc /tmp/nanorc.bak
echo "# l06 marker" | sudo tee -a /etc/nanorc
apt-get -s remove nano
```

> Chỉ **mô phỏng** remove `nano` nếu bạn đang dùng nó làm editor. Nếu muốn làm thật, dùng VM disposable: `sudo apt remove nano` → `ls -l /etc/nanorc` (còn, có marker) → `dpkg -l nano` (`rc`) → `sudo apt purge nano` → `/etc/nanorc` mất → `sudo apt install nano`.

Khôi phục: `sudo cp /tmp/nanorc.bak /etc/nanorc`.

## Bước 5 — Lịch sử

```bash
grep -A4 'tree' /var/log/apt/history.log | tail -20
```

---

## Definition of Done

- [ ] Bảng version: installed / candidate / có sẵn.
- [ ] Evidence hold chặn upgrade (mô phỏng).
- [ ] Rollback thật **hoặc** ghi rõ vì sao không rollback được.
- [ ] Giải thích `remove` vs `purge` bằng trạng thái `rc` và conffile.
- [ ] Trích `history.log` cho các thay đổi đã làm.

## Cleanup

`sudo apt-mark unhold tree`; trả `/etc/nanorc` về bản backup; gỡ `tree` nếu ban đầu chưa có.
