# L06-02 — Package inventory và mô phỏng thay đổi

## Mục tiêu

Học cách xem package trước khi thay đổi hệ thống. Bài này ưu tiên mô phỏng.

### 1. Chọn một package đã có

```bash
dpkg-query -W -f='${binary:Package}\t${Version}\n' | sort | head -n 20
```

Chọn package nhỏ, không phải kernel, systemd, ssh hoặc sudo. Gọi nó là `<PACKAGE>`.

### 2. Thu thập metadata

```bash
apt show <PACKAGE>
dpkg -s <PACKAGE>
dpkg -L <PACKAGE> | head -n 30
```

Tìm version, architecture, dependency, maintainer và một số file package cung cấp.

### 3. Mô phỏng upgrade/remove

```bash
apt-get -s install --only-upgrade <PACKAGE>
apt-get -s remove <PACKAGE>
```

`-s` chỉ mô phỏng, không thay đổi hệ thống. Nếu thấy package quan trọng trong danh sách bị gỡ, dừng lại.

### 4. Tìm package từ file

```bash
FILE_PATH="$(dpkg -L <PACKAGE> | awk '/^\/usr\/bin\// {print; exit}')"
printf 'Selected file: %s\n' "$FILE_PATH"
dpkg -S "$FILE_PATH"
```

## DoD

- [ ] Đọc được metadata của package.
- [ ] Biết phân biệt mô phỏng với thay đổi thật.
- [ ] Giải thích được dependency và file ownership.
- [ ] Không làm thay đổi package trong bài này.
