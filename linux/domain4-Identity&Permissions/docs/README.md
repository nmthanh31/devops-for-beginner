# L04 — Identity & Permissions · Theory

## Nguồn và ranh giới LPIC-1

Nội dung cốt lõi được diễn giải từ các objective chính thức:

- **104.5:** quyền và ownership trên file/thư mục, special bits, `umask`, dùng group để chia sẻ quyền.
- **107.1:** user/group account và các cơ sở dữ liệu hệ thống liên quan.
- **110.1:** nhận diện file SUID/SGID, password aging và basic sudo configuration/usage.

**PAM** và **ACL** được roadmap yêu cầu ở mức hiểu luồng/nhận diện, nhưng không thuộc các key knowledge areas nêu trên; chúng được đánh dấu là phần mở rộng, không gán nhầm là core LPIC-1.

Nguồn: [LPIC-1 Objectives V5.0 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0), [LPIC-1 Learning Material 101](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf), [LPIC-1 Learning Material 102](https://learning.lpi.org/pdfstore/LPI-Learning-Material-102-500-en.pdf).

## Thứ tự học

1. [User, group và identity](./01-users-groups-identity.md)
2. [Owner, group và rwx](./02-ownership-and-rwx.md)
3. [`umask` và special permission bits](./03-umask-special-bits.md)
4. [Access check và chẩn đoán permission](./04-access-check-troubleshooting.md)
5. [`sudo`, PAM và ACL](./05-sudo-pam-acl.md)
6. [Command reference](./00-command-reference.md)

## Mô hình tư duy

~~~text
process credentials: UID + primary/supplementary GID
                 ↓ kernel checks
directory path:  x/search trên từng parent directory
                 ↓
target inode:     owner/group + mode bits (+ ACL nếu có)
                 ↓
decision:         allow / deny
~~~

Một service có thể có permission đúng trên file cuối nhưng vẫn bị từ chối vì thiếu quyền `x` trên một parent directory, chạy dưới UID khác dự kiến, hoặc có ACL làm thay đổi kết quả.

