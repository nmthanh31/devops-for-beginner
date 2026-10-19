# Bài 5 — `sudo`, PAM và ACL

## `sudo`: chạy một command với quyền được cấp

`sudo command` yêu cầu policy cho phép user hiện tại chạy command đó dưới một identity khác — mặc định thường là root. `sudo -l` liệt kê quyền mà policy cấp cho user hiện tại.

~~~bash
sudo -l
sudo -u appuser id
~~~

`sudo` không có nghĩa “user này trở thành root vĩnh viễn”; quyền áp dụng theo command/session và cấu hình. Không chỉnh `/etc/sudoers` bằng editor thường vì lỗi cú pháp có thể khóa quyền quản trị. Dùng `visudo`, hoặc công cụ quản lý policy của distro.

LPIC-1 đưa basic sudo configuration/usage vào objective 110.1. Trong theory này, trọng tâm là đọc `sudo -l`, hiểu command chạy dưới identity nào và không dùng sudo rộng hơn cần thiết.

## PAM — luồng xác thực có thể cấu hình (mở rộng roadmap)

PAM (Pluggable Authentication Modules) là framework mà ứng dụng như login/sshd/sudo có thể gọi để xác thực và thiết lập session. Thay vì mỗi ứng dụng tự viết cơ chế password, ứng dụng gọi PAM; PAM chạy các module theo policy cấu hình.

Bốn module type dễ nhận ra:

| Type | Câu hỏi dễ nhớ |
|---|---|
| `auth` | Người dùng chứng minh danh tính ra sao? |
| `account` | Account có được phép dùng service lúc này không — ví dụ hết hạn/giới hạn? |
| `password` | Cập nhật authentication token/password như thế nào? |
| `session` | Việc gì cần làm khi mở/đóng session — ví dụ logging hoặc setup session? |

Các module được xếp thành stack; control flags như `required`, `requisite`, `sufficient`, `optional` quyết định cách kết quả từng module ảnh hưởng toàn bộ stack. Vì vậy, lỗi login không nhất thiết chỉ do password sai: account policy hoặc session setup cũng có thể thất bại.

**Không chỉnh file PAM trong bài học này.** Sai một dòng có thể làm hỏng login/sudo. Chỉ đọc cấu hình và hiểu rằng ứng dụng → PAM service policy → module stack → kết quả access/session.

PAM là phần roadmap yêu cầu hiểu flow; nó không được nêu trong các key knowledge areas 104.5/107.1/110.1 của LPIC-1 V5.0, nên coi là mở rộng nền tảng vận hành.

## ACL — quyền bổ sung ngoài ba class cơ bản (nhận biết)

Traditional mode bits có owner/group/other. POSIX ACL có thể thêm quyền cho một user hoặc group cụ thể. Dấu `+` ở cuối permission trong `ls -l` thường báo có ACL mở rộng; dùng `getfacl` để xem toàn bộ.

~~~text
-rw-r-----+ 1 appuser appteam ... report.txt
~~~

ACL có `mask` giới hạn quyền hiệu lực của các named user/group và group class. Vì vậy, đừng suy luận toàn bộ access chỉ từ `ls -l`; khi thấy dấu `+`, kiểm tra ACL. Trong roadmap L04 chỉ cần nhận diện và đọc; cấu hình ACL chi tiết để phần lab/extension.

ACL không nằm trong danh sách command cốt lõi LPIC 104.5 nêu ra; đây là phần mở rộng vận hành để xử lý shared access thực tế. ([acl(5)](https://man7.org/linux/man-pages/man5/acl.5.html))

## Nguồn

- [LPIC-1 Objectives V5.0 — 110.1](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [Linux-PAM System Administrator's Guide](https://github.com/linux-pam/linux-pam/blob/master/doc/sag/Linux-PAM_SAG.xml)
- [Linux-PAM `pam.conf` syntax](https://github.com/linux-pam/linux-pam/blob/master/doc/man/pam.conf-syntax.xml)
- [POSIX ACL overview — `acl(5)`](https://man7.org/linux/man-pages/man5/acl.5.html)

