# L08-03 — `diagnose.sh` với exit code có nghĩa và 8 test

| | |
|---|---|
| **Thời lượng** | 90 phút |
| **Môi trường** | VM lab, Bash, `shellcheck` (nếu có). Làm trong `~/l08-lab/diag` |
| **Mục tiêu** | Script chẩn đoán một service HTTP local theo 4 lớp, exit code phân biệt từng lớp lỗi, có 8 test tự động |
| **Competency L08** | "diagnose.sh an toàn với exit code có nghĩa — 8 tests + cleanup + no secret" |

## Đặc tả

```text
Usage: diagnose.sh UNIT PORT [PATH]
Kiểm theo thứ tự, dừng ở lớp lỗi đầu tiên:
  1. unit active?          → exit 10 nếu không
  2. có listener PORT?     → exit 11 nếu không
  3. HTTP PATH trả 2xx/3xx → exit 12 nếu không
  OK                       → exit 0
Lỗi dùng sai (thiếu arg, PORT không phải số 1–65535) → exit 2
In một dòng tóm tắt ra stdout, chi tiết ra stderr. Không in env/secret.
```

## Bước 1 — Viết script

Tự viết trước 30 phút. Yêu cầu: strict mode, quote mọi biến, validate input, `trap` cleanup file tạm, timeout cho `curl`.

<details>
<summary>Bản tham khảo (mở sau khi tự viết)</summary>

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

usage() { echo "Usage: ${0##*/} UNIT PORT [PATH]" >&2; exit 2; }
[[ $# -ge 2 && $# -le 3 ]] || usage
unit=$1 port=$2 path=${3:-/}
[[ $port =~ ^[0-9]+$ ]] && (( port >= 1 && port <= 65535 )) || usage
[[ $path == /* ]] || usage

tmp=$(mktemp); trap 'rm -f -- "$tmp"' EXIT

if ! systemctl --user is-active --quiet -- "$unit" && ! systemctl is-active --quiet -- "$unit"; then
  echo "FAIL unit: $unit not active"; exit 10
fi
if ! ss -Hlnt "sport = :$port" | grep -q .; then
  echo "FAIL listen: nothing on :$port"; exit 11
fi
code=$(curl -s -o "$tmp" -w '%{http_code}' --max-time 3 "http://127.0.0.1:$port$path" || true)
if [[ ! $code =~ ^[23] ]]; then
  echo "FAIL http: $path -> ${code:-no response}"; head -c 200 "$tmp" >&2 || true; exit 12
fi
echo "OK $unit :$port $path -> $code"
```

</details>

## Bước 2 — Service lab để test

```bash
mkdir -p ~/l08-lab/diag/www && echo ok > ~/l08-lab/diag/www/healthz
systemd-run --user --unit=l08-web -p WorkingDirectory="$HOME/l08-lab/diag/www" python3 -m http.server 18088 --bind 127.0.0.1
```

## Bước 3 — 8 test

Viết `test.sh` chạy từng case và so exit code mong đợi:

| # | Case | Lệnh | Exit mong đợi |
|---|---|---|---|
| 1 | Khỏe | `./diagnose.sh l08-web 18088 /healthz` | 0 |
| 2 | Path không có | `./diagnose.sh l08-web 18088 /nope` | 12 |
| 3 | Sai port | `./diagnose.sh l08-web 18099` | 11 |
| 4 | Unit không tồn tại | `./diagnose.sh khong-co 18088` | 10 |
| 5 | Thiếu argument | `./diagnose.sh` | 2 |
| 6 | Port không phải số | `./diagnose.sh l08-web abc` | 2 |
| 7 | Port ngoài dải | `./diagnose.sh l08-web 70000` | 2 |
| 8 | Argument có khoảng trắng/ký tự lạ | `./diagnose.sh 'a b; rm -rf ~' 18088` | 10 (và **không** chạy gì khác) |

```bash
run() { local want=$1; shift; "$@" >/dev/null 2>&1; local got=$?; [[ $got == "$want" ]] && echo "PASS $want $*" || { echo "FAIL want=$want got=$got $*"; fails=$((fails+1)); }; }
fails=0
run 0  ./diagnose.sh l08-web 18088 /healthz
run 12 ./diagnose.sh l08-web 18088 /nope
# ... 6 case còn lại
exit $fails
```

## Bước 4 — Chất lượng

```bash
shellcheck diagnose.sh test.sh
bash -n diagnose.sh
grep -nEi 'password|token|secret|env$' diagnose.sh || echo "không in secret"
```

---

## Definition of Done

- [ ] 8/8 test PASS, `test.sh` trả exit 0.
- [ ] ShellCheck sạch (hoặc giải thích từng cảnh báo bỏ qua).
- [ ] Exit code mỗi lớp khác nhau và có trong usage/README.
- [ ] Không in env/secret; file tạm được `trap` dọn.
- [ ] Case 8 chứng minh input độc hại không bị thực thi.

## Cleanup

```bash
systemctl --user stop l08-web
rm -r ~/l08-lab/diag
```
