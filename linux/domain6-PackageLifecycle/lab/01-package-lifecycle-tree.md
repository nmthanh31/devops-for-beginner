# L06-01 — Package lifecycle với `tree`

## Mục tiêu

Thực hành vòng đời một package nhỏ:

```text
search → inspect → install → verify → inspect files → remove → verify
```

## Bài làm

### 1. Kiểm tra trạng thái ban đầu

```bash
cat /etc/os-release
apt-cache policy tree
dpkg -s tree 2>/dev/null || echo "tree is not installed"
```

Ghi lại distro, version candidate và package đã cài hay chưa.

### 2. Cập nhật package index

```bash
sudo apt update
```

Giải thích sự khác nhau giữa `apt update` và cài package. Nếu repository lỗi, ghi lại.

### 3. Cài package

```bash
sudo apt install tree
```

Trước khi gõ `Y`, đọc danh sách package sẽ được cài, nâng cấp hoặc gỡ.

### 4. Verify package

```bash
dpkg -s tree
command -v tree
tree --version
dpkg -L tree
dpkg -S "$(command -v tree)"
```

Ghi lại status/version, executable path, file list và package sở hữu executable.

### 5. Gỡ package và kiểm tra

```bash
sudo apt remove tree
dpkg -s tree 2>&1 || true
command -v tree || echo "tree command is no longer available"
```

Không dùng `purge` trong lần đầu để phân biệt `remove` với `purge`.

## DoD

- [ ] Giải thích được `apt update` khác `apt install`.
- [ ] Biết dùng `dpkg -L` và `dpkg -S`.
- [ ] Xác nhận được package đã cài và đã gỡ.
- [ ] Không có package hệ thống ngoài `tree` bị thay đổi.
