# L04 Lab — Least privilege cho một service, sửa lỗi quyền không dùng 777

| | |
|---|---|
| **Thời lượng** | 75 phút |
| **Môi trường** | VM lab, `sudo`. Chỉ tạo tài nguyên tên `l04*` |
| **Mục tiêu** | Một "service" chạy dưới `l04app` đọc config, ghi data; tạo 4 lỗi quyền, chẩn đoán bằng evidence, sửa tối thiểu |
| **Cấm** | `chmod 777`, chạy service bằng root để "cho chạy" |

```text
/srv/l04/            root:l04team  2750 (SGID)
├── conf/app.conf    root:l04team  0640   ← l04app chỉ cần đọc
└── data/            l04app:l04team 2770  ← l04app ghi
```

## Bước 0 — Dựng

```bash
getent passwd l04app || sudo useradd --system --no-create-home --shell /usr/sbin/nologin l04app
getent group l04team || sudo groupadd l04team
sudo usermod -aG l04team l04app
sudo install -d -o root   -g l04team -m 2750 /srv/l04
sudo install -d -o root   -g l04team -m 2750 /srv/l04/conf
sudo install -d -o l04app -g l04team -m 2770 /srv/l04/data
echo "greeting=hello" | sudo tee /srv/l04/conf/app.conf >/dev/null
sudo chown root:l04team /srv/l04/conf/app.conf && sudo chmod 0640 /srv/l04/conf/app.conf
```

"Service" giả lập — một lệnh chạy dưới `l04app`:

```bash
l04run() { sudo -u l04app sh -c 'cat /srv/l04/conf/app.conf && date >> /srv/l04/data/out.log && echo OK'; }
l04run
```

**Baseline:** ghi output `l04run`, `namei -l /srv/l04/data/out.log`, `stat -c '%A %a %U:%G %n' /srv/l04 /srv/l04/conf /srv/l04/conf/app.conf /srv/l04/data`.

**Negative test baseline:** một user khác (ví dụ `nobody`) **không** đọc được config:

```bash
sudo -u nobody cat /srv/l04/conf/app.conf   # phải Permission denied
```

## Bước 1 — 4 lỗi, làm từng cái

Với **mỗi** lỗi: chạy lệnh tạo lỗi → `l04run` → viết hypothesis → thu ≥ 2 evidence → sửa **một** thay đổi → `l04run` OK + negative test vẫn denied → ghi vào bảng.

| # | Tạo lỗi (người khác làm hoặc tự làm rồi quên) | Gợi ý evidence |
|---|---|---|
| F1 | `sudo chmod 2740 /srv/l04` | `namei -l` |
| F2 | `sudo chmod 0600 /srv/l04/conf/app.conf` | `stat` file cuối, class nào được chọn |
| F3 | `sudo gpasswd -d l04app l04team` | `id l04app` |
| F4 | `sudo chown root:root /srv/l04/data && sudo chmod 0755 /srv/l04/data` | `stat` dir data, thao tác tạo/ghi |

<details>
<summary>Đáp án tham khảo (mở sau khi tự làm)</summary>

- F1: group mất `x` trên `/srv/l04` → không traverse. Sửa `chmod 2750 /srv/l04`.
- F2: group mất `r` trên config. Sửa `chmod 0640`.
- F3: `l04app` không còn trong `l04team` → rơi vào class other. Sửa `usermod -aG l04team l04app`.
- F4: data không còn ghi được bởi l04app. Sửa `chown l04app:l04team` + `chmod 2770`.

</details>

## Bước 2 — SGID và umask

```bash
sudo -u l04app sh -c 'umask 027; touch /srv/l04/data/new.txt'
stat -c '%A %U:%G %n' /srv/l04/data/new.txt
```

Giải thích: vì sao group là `l04team`? Vì sao mode là `640`?

## Bước 3 — ACL (nhận diện)

```bash
sudo setfacl -m u:nobody:r /srv/l04/conf/app.conf
ls -l /srv/l04/conf/app.conf      # có dấu +
getfacl /srv/l04/conf/app.conf
sudo -u nobody cat /srv/l04/conf/app.conf   # vẫn denied? vì sao? (gợi ý: /srv/l04 có cho nobody x không)
sudo setfacl -b /srv/l04/conf/app.conf      # gỡ ACL
```

---

## Definition of Done

- [ ] Baseline + negative baseline.
- [ ] Bảng 4 fault: hypothesis, 2 evidence, fix một thay đổi, positive + negative verify.
- [ ] Giải thích SGID + umask ở bước 2.
- [ ] Giải thích kết quả ACL ở bước 3 (parent dir vẫn chặn).
- [ ] Không có `777`, không chạy bằng root.

## Cleanup

```bash
sudo rm -r /srv/l04
sudo userdel l04app
sudo groupdel l04team
getent passwd l04app; getent group l04team; ls -d /srv/l04 2>/dev/null || echo "sạch"
```
