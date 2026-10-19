# Bài 4 — Access check và chẩn đoán permission

> **Kết nối L01–L03:** dùng identity process và path/inode để giải thích vì sao service đọc/ghi được hoặc bị từ chối.

## Quyền trên file cuối chưa đủ

Để process mở `/srv/app/config/app.env`, nó cần đi qua các directory component. Thông thường cần quyền `x` (search) trên từng directory cha, rồi quyền phù hợp trên file cuối.

~~~text
/                 cần traverse
/srv              cần traverse
/srv/app          cần traverse
/srv/app/config   cần traverse
app.env           cần read hoặc write tùy thao tác
~~~

`ls -l /srv/app/config/app.env` chỉ mô tả path cuối; không cho biết đầy đủ quyền trên mọi parent directory.

## Checklist khi gặp `Permission denied`

1. **Process thực tế chạy với ai?** Lấy UID/GID và supplementary groups của process, không đoán theo user đang login.
2. **Path nào đang được truy cập?** Xác định chính xác absolute path và thao tác (read/write/execute).
3. **Từng parent directory có traverse được không?** Kiểm tra owner/group/mode dọc path.
4. **File cuối có đúng owner/group/mode không?** Đừng chỉ nhìn tên username; đối chiếu UID/GID số nếu cần.
5. **Có ACL hoặc lớp policy khác không?** Dấu `+` trong `ls -l` là tín hiệu cần `getfacl`; SELinux/AppArmor/container mount có thể là lớp khác nhưng thuộc phần mở rộng.
6. **Sau thay đổi group, process đã nhận group mới chưa?** Process đang chạy thường giữ credentials hiện tại; service/session có thể cần khởi động lại theo change plan để nạp identity mới.

## Evidence commands

~~~bash
id
ps -o pid,user,group,uid,gid,cmd -p PID
stat -c '%A %a %U:%G %u:%g %n' /path/to/file
namei -l /path/to/file
getfacl /path/to/file
sudo -l
~~~

Thay `PID` và path bằng đối tượng thật. `namei -l` giúp thấy từng component; `stat` cho metadata của object cuối; `id` cho identity shell hiện tại. Identity shell không nhất thiết giống identity của service.

## Least privilege cho service

Nguyên tắc: service chỉ có quyền cần cho chức năng của nó. Ví dụ API cần đọc config và ghi thư mục data riêng thì cấp group/quyền tương ứng cho hai path đó; không giải quyết bằng `chmod -R 777` hoặc chạy service bằng root.

~~~text
service UID/GID
  ├── config: read
  ├── application binary: execute/read
  ├── data directory: write/search
  └── unrelated home/secrets: no access
~~~

Mỗi quyền nên có lý do và đường kiểm chứng. Sau khi thay đổi, kiểm tra cả đường được phép lẫn đường phải bị từ chối.

## Nguồn

- [LPIC-1 Objectives V5.0 — 104.5](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- Tham khảo công cụ: `man namei`, `man stat`, `man id`, `man getfacl`
- SELinux/AppArmor và container mount policy là phần mở rộng, chưa đi sâu trong L04.

