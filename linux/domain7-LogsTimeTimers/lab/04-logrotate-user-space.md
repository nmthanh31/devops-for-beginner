# L07-04 — Logrotate trong user space và bẫy FD cũ

| | |
|---|---|
| **Thời lượng** | 40 phút |
| **Môi trường** | VM lab có `logrotate`; chạy hoàn toàn trong `~/l07rot`, không sửa `/etc/logrotate.d` |
| **Mục tiêu** | Rotate một log thật, chứng minh bẫy "app vẫn ghi file cũ", sửa bằng `copytruncate` hoặc reopen |

## Bước 1 — "App" ghi log liên tục

```bash
mkdir -p ~/l07rot && cd ~/l07rot
( exec >> app.log; while true; do date +%T; sleep 1; done ) &
APP=$!; echo "app pid=$APP"
sleep 3; ls -l app.log
```

> Subshell mở `app.log` **một lần** (`exec >>`) rồi ghi mãi qua FD đó — giống daemon thật.

## Bước 2 — Config rotate (kiểu đổi tên)

```bash
cat > rot.conf <<EOF
$HOME/l07rot/app.log {
    rotate 3
    size 1
    missingok
    compress
    delaycompress
}
EOF
logrotate -d -s state rot.conf      # dry run — đọc kế hoạch
logrotate -f -s state rot.conf      # làm thật
sleep 3; ls -l; ls -l /proc/$APP/fd/1
```

**Dự đoán trước:** file nào lớn dần sau rotate — `app.log` hay `app.log.1`?

**Kết quả mong đợi:** `app.log` không còn/không tăng; `app.log.1` tiếp tục tăng; `/proc/$APP/fd/1` trỏ tới `app.log.1`. Đây là bẫy FD cũ.

## Bước 3 — Sửa bằng `copytruncate`

```bash
sed -i 's/delaycompress/delaycompress\n    copytruncate/' rot.conf
logrotate -f -s state rot.conf
sleep 3; ls -l; ls -l /proc/$APP/fd/1
```

**Kết quả mong đợi:** `app.log` bị truncate rồi tăng lại; FD vẫn trỏ `app.log`.

Ghi chú: với daemon thật, cách tốt hơn thường là `postrotate` gửi signal để nó **reopen** (ví dụ `systemctl kill -s HUP svc` hoặc `nginx -s reopen`) — không mất dòng log như `copytruncate`.

---

## Definition of Done

- [ ] Dry run (`-d`) đọc được trước khi chạy thật.
- [ ] Evidence bẫy FD: `ls -l` + `/proc/PID/fd/1` sau rotate kiểu đổi tên.
- [ ] Evidence sau `copytruncate`.
- [ ] Giải thích vì sao cần `postrotate` reopen hoặc `copytruncate`, và rủi ro của `copytruncate`.

## Cleanup

```bash
kill $APP; cd ~ && rm -r ~/l07rot
```
