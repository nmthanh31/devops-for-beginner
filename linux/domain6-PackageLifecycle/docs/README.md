# L06 — Package Lifecycle · Theory

## Nguồn và phạm vi

Phần cốt lõi đối chiếu [LPIC-1 Objectives V5.0 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0):

- **102.4 — Debian package management:** cài, cập nhật, gỡ package Debian; xem version, content, dependency, integrity và installation status; nhận biết `apt`.
- **102.5 — RPM/YUM package management:** cài, cập nhật, gỡ package RPM; xem version, dependency, integrity, signature và file do package cung cấp; nhận biết `dnf`.

## Thứ tự học

1. [Package, repository và metadata](./01-package-repository-metadata.md)
2. [APT và dependency](./02-apt-repository-dependencies.md)
3. [DPKG và package database](./03-dpkg-package-database.md)
4. [Vòng đời package](./04-package-lifecycle.md)
5. [Lỗi, repair và rollback](./05-package-repair-rollback.md)
6. [RPM, YUM và DNF](./06-rpm-yum-dnf.md)
7. [Command reference](./00-command-reference.md)

## Mô hình tư duy

```text
Tìm package
    ↓
Chọn version và repository
    ↓
Giải quyết dependency
    ↓
Cài file + ghi package database
    ↓
Cấu hình package/service
    ↓
Verify process, config và behaviour
```

