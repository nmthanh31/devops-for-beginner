# L12 Lab — Backup, verify, restore

| | |
|---|---|
| **Thời lượng** | 60 phút |
| **Phạm vi** | Chỉ trong `~/l12-lab` trên VM. Không dùng data thật hay database đang chạy |
| **Mục tiêu** | Tạo backup có hash → restore vào staging → chứng minh khớp → negative test phát hiện sai lệch → runbook |

## Bước 1 — Dữ liệu nguồn

```bash
mkdir -p ~/l12-lab/{source/sub,backup,restore}
cd ~/l12-lab
echo "config v1"         > source/app.conf
echo "order 1001"        > source/sub/orders.txt
printf 'secret=lab-only\n' > source/.env && chmod 600 source/.env
find source -type f -exec stat -c '%a %U %n' {} \;
```

## Bước 2 — Backup + hash

```bash
date -u +%FT%TZ | tee backup/created.txt
tar -czf backup/source.tar.gz -C ~/l12-lab source
sha256sum backup/source.tar.gz | tee backup/source.tar.gz.sha256
```

> Đọc lệnh: `-C ~/l12-lab` đổi thư mục trước khi thêm `source` → archive chứa path tương đối `source/...`.

## Bước 3 — Kiểm trước khi restore

```bash
sha256sum -c backup/source.tar.gz.sha256
tar -tzvf backup/source.tar.gz          # có path tuyệt đối "/" hoặc "../" không?
```

## Bước 4 — Restore vào staging và so sánh

```bash
time tar -xzf backup/source.tar.gz -C restore
diff -r source restore/source && echo "NỘI DUNG KHỚP"
find restore/source -type f -exec stat -c '%a %U %n' {} \;   # so mode .env = 600?
(cd source && find . -type f -exec sha256sum {} \; | sort -k2) > /tmp/l12-a
(cd restore/source && find . -type f -exec sha256sum {} \; | sort -k2) > /tmp/l12-b
diff /tmp/l12-a /tmp/l12-b && echo "HASH TỪNG FILE KHỚP"
```

## Bước 5 — Negative test

**Dự đoán:** sửa một file trong restore, `diff -r` và `sha256sum -c` (của archive) báo gì?

```bash
echo "tampered" >> restore/source/sub/orders.txt
diff -r source restore/source; echo "diff exit=$?"
sha256sum -c backup/source.tar.gz.sha256      # vẫn OK — vì sao?
```

Khôi phục lại vào **thư mục thử mới**:

```bash
mkdir restore2 && tar -xzf backup/source.tar.gz -C restore2 && diff -r source restore2/source && echo OK
```

## Bước 6 — Runbook + phân tích

Viết runbook theo [mẫu Bài 3](../docs/03-recovery-runbook.md#mẫu-runbook-copy-và-điền). Trả lời:

1. Backup nằm cùng VM bảo vệ được sự cố nào, chưa bảo vệ được sự cố nào?
2. Nếu sự cố xảy ra 2 giờ sau `created.txt`, RPO thực tế là bao nhiêu?
3. `time` ở bước 4 cho RTO phần restore là bao nhiêu? RTO thật sẽ cộng thêm gì?

---

## Definition of Done

- [ ] Cây file, archive listing, hash archive, `sha256sum -c` OK.
- [ ] `diff -r` + hash từng file + mode `.env` khớp sau restore.
- [ ] Negative test: `diff` phát hiện sai; giải thích vì sao hash archive vẫn OK.
- [ ] Runbook + 3 câu phân tích RPO/RTO/failure domain.

## Cleanup

```bash
cd ~ && ls -d ~/l12-lab && rm -r ~/l12-lab   # xác nhận đúng thư mục trước khi xóa
rm -f /tmp/l12-a /tmp/l12-b
```

Không dùng glob hoặc biến có thể rỗng trong lệnh xóa.
