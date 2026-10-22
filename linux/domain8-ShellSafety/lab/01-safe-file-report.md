# L08-01 — Safe file report script

## Mục tiêu

Viết script Bash có quoting, validation, exit status, `trap`, dry-run và report. Script chỉ làm việc trong thư mục lab.

### 1. Chuẩn bị dữ liệu

```bash
LAB_DIR="$HOME/l08-lab"
mkdir -p "$LAB_DIR/input"
printf 'alpha\n' > "$LAB_DIR/input/one.txt"
printf 'beta\n' > "$LAB_DIR/input/file with spaces.txt"
```

### 2. Yêu cầu script

Tạo `safe-report.sh` với các yêu cầu:

- Có shebang Bash.
- Dùng `set -Eeuo pipefail`.
- Nhận một input directory từ argument.
- Từ chối nếu thiếu argument.
- Từ chối nếu path không tồn tại hoặc không phải directory.
- Dùng quote cho biến/path.
- Tạo output trong chính `$HOME/l08-lab/output`.
- Ghi danh sách file regular và kích thước vào report.
- Có `--dry-run` để chỉ in hành động, không ghi report.
- Có `trap` để ghi thông báo cleanup khi script kết thúc.
- Trả exit code khác 0 khi input sai.

### 3. Test bắt buộc

```bash
bash safe-report.sh --dry-run "$HOME/l08-lab/input"
printf 'dry-run exit=%s\n' "$?"

bash safe-report.sh "$HOME/l08-lab/input"
printf 'normal exit=%s\n' "$?"

bash safe-report.sh
printf 'missing-arg exit=%s\n' "$?"

bash safe-report.sh "$HOME/l08-lab/no-such-dir"
printf 'bad-path exit=%s\n' "$?"
```

Kiểm tra file có khoảng trắng được xử lý đúng.

### 4. Evidence

Ghi lại input, exit code từng test, sự khác nhau giữa dry-run/normal run và nội dung report.

## DoD

- [ ] Input hợp lệ chạy thành công.
- [ ] Input thiếu/sai bị từ chối.
- [ ] File có khoảng trắng không bị tách sai.
- [ ] Dry-run không tạo report.
- [ ] Script không ghi/xóa ngoài `$HOME/l08-lab`.
