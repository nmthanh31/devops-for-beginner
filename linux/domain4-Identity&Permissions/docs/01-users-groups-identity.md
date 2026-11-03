# Bài 1 — User, group và process identity

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Giải thích kernel quyết định quyền theo **UID/GID số của process**, không theo username trên terminal.
> - Đọc account qua `id`, `getent` (NSS) thay vì chỉ grep `/etc/passwd`.
> - Phân biệt human account và service account.
>
> **Hình dung:** username như tên trên thẻ nhân viên, UID là **mã số** trên chip thẻ — cửa từ (kernel) chỉ đọc mã số. Service chạy bằng thẻ của chính nó, không phải thẻ của admin đã bấm `systemctl start`.


> **LPIC-1 107.1:** quản lý user/group và hiểu các file cơ sở dữ liệu liên quan. Bài này tập trung vào cách identity của process ảnh hưởng đến quyền truy cập.

## Linux kiểm tra UID/GID, không chỉ username

Username và group name là nhãn dễ đọc. Kernel ra quyết định chủ yếu dựa trên số định danh:

- **UID**: định danh user.
- **GID**: định danh group.
- **Primary group**: group mặc định gắn với account.
- **Supplementary groups**: các group bổ sung mà user/process là thành viên.

Process giữ credentials. Khi process mở file, quyền được xét theo credentials của process tại thời điểm truy cập, không theo username của người đang nhìn terminal.

~~~text
user setup chạy systemctl
       ↓ systemd tạo service process
service process có UID/GID của cấu hình service
       ↓ kernel so credentials này với owner/group/mode của file
allow hoặc deny
~~~

Vì vậy, admin có thể đọc file bằng tài khoản của mình trong terminal, nhưng service chạy dưới account khác vẫn bị `Permission denied`.

## Account database và NSS

Các file truyền thống:

| File | Vai trò |
|---|---|
| `/etc/passwd` | Thông tin account như username, UID, primary GID, home, shell; trường password thường là placeholder `x` |
| `/etc/shadow` | Thông tin xác thực nhạy cảm và password aging; thường chỉ root được đọc |
| `/etc/group` | Group name, GID và danh sách thành viên được khai báo |
| `/etc/skel/` | File mẫu được dùng khi tạo home cho user mới |

Máy có thể lấy account từ nhiều nguồn như local files hoặc directory service. `getent` hỏi qua NSS nên thường đáng tin hơn việc chỉ grep `/etc/passwd`.

~~~bash
id
id someuser
getent passwd someuser
getent group somegroup
groups
~~~

Không in/chia sẻ nội dung `/etc/shadow` trong ticket hoặc chat; đó là dữ liệu xác thực nhạy cảm.

## User thường và service account

- **Human account** thường có home, shell đăng nhập và quyền tương tác.
- **Service account** dành cho một daemon/application; nên có quyền tối thiểu cần thiết và thường không cần shell đăng nhập tương tác.

Nếu service chỉ cần đọc một cấu hình và ghi vào một thư mục data, hãy cấp quyền đúng cho account/group đó trên đúng path, thay vì chạy service dưới root hoặc mở quyền rộng cho tất cả.

## LPIC cần nhận biết

107.1 bao gồm thêm thao tác tạo/sửa/xóa user và group, account hạn chế, `passwd`, `chage`, `useradd`, `usermod`, `userdel`, `groupadd` và các file account. Trong buổi này, trước hết hãy đọc identity/evidence; thay đổi account hệ thống sẽ để dành cho lab có kiểm soát.

<!-- learn:tail -->
## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Tôi đọc được file thì service cũng đọc được." | Service chạy UID/GID khác. |
| "Thêm user vào group là có hiệu lực ngay." | Process/session đang chạy giữ credentials cũ; cần login/restart lại. |
| "`grep /etc/passwd` là đủ." | Account có thể đến từ LDAP/SSSD; dùng `getent`. |

## Tự kiểm tra

1. Đổi username `alice` thành `alice2` nhưng giữ UID 1001. File cũ của alice thuộc ai?
2. `usermod -aG appteam setup` xong, `id` trong terminal cũ chưa thấy `appteam`. Vì sao?

<details>
<summary>Đáp án</summary>

1. Vẫn thuộc UID 1001 → hiển thị `alice2`.
2. Shell hiện tại giữ supplementary groups lúc login; mở session mới (hoặc `newgrp`).

</details>

## Nguồn

- [LPIC-1 Objectives V5.0 — 107.1](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [LPIC-1 Learning Material 102 — lesson 107.1](https://learning.lpi.org/pdfstore/LPI-Learning-Material-102-500-en.pdf)
- Tham khảo lệnh và file: `man passwd`, `man group`, `man shadow`, `man getent`, `man id`

