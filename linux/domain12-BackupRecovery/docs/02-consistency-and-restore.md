# Bài 2 — Tính nhất quán, kiểm tra và restore

> **Sau bài này bạn sẽ:**
> - Phân biệt crash-consistent và application-consistent.
> - Chọn đúng công cụ `tar` / `rsync` / `dd` và biết rủi ro của từng cái.
> - Biết checksum chứng minh gì và **không** chứng minh gì; chạy restore drill 7 bước.
>
> **Cần trước:** [Bài 1](./01-backup-design.md).

## Tính nhất quán là gì?

Backup **crash-consistent** giống dữ liệu sau khi máy mất điện: filesystem có thể phục hồi nhưng ứng dụng cần replay journal hoặc tự sửa state. Backup **application-consistent** được tạo khi ứng dụng/database đã flush hoặc dùng cơ chế snapshot/backup riêng để các file liên quan khớp nhau.

Copy file database đang ghi liên tục bằng `tar` hoặc `rsync` có thể tạo bản sao không nhất quán. Với database, dùng công cụ backup/export do database hỗ trợ hoặc dừng/đóng băng ghi có kiểm soát.

Ví dụ ứng dụng ghi `orders.db` và `uploads/` liên tục. Nếu copy `orders.db` lúc 10:01 rồi `uploads/` lúc 10:05, backup có thể chứa record tham chiếu file chưa có hoặc ngược lại. Hash của cả hai file vẫn hợp lệ: hash chỉ chứng minh bản sao không đổi sau khi tạo, không chứng minh hai thành phần nhất quán với nhau. Muốn khôi phục đáng tin, cần điểm nhất quán chung hoặc cơ chế backup do ứng dụng/database hỗ trợ.

## `tar`, `rsync`, `dd` khác nhau thế nào?

| Công cụ | Làm gì | Hợp với | Rủi ro chính |
|---|---|---|---|
| `tar` | Đóng gói cây file + metadata | Config, tập file, archive | Path tương đối sai do `-C`/working dir |
| `rsync` | Đồng bộ hai cây, chỉ chuyển phần khác | Mirror, backup tăng dần | `--delete` + destination nhầm = **xóa dữ liệu**; dấu `/` cuối |
| `dd` | Sao chép block/byte | Image cả disk/partition | Đảo `if`/`of` = **ghi đè disk** |
| Tool của DB (`pg_dump`...) | Export nhất quán | Database | Phải kiểm restore được |

Một archive có thể tồn tại nhưng chứa thiếu file, sai quyền hoặc không đọc được. Kiểm tra phải gồm nội dung và khả năng restore.

## Checksum chứng minh điều gì?

`sha256sum` tính hash của file. Nếu hash sau khi chuyển/cất giữ giống hash ban đầu, file chưa bị thay đổi trong phạm vi so sánh. Hash không tự chứng minh dữ liệu bên trong đã nhất quán hoặc ứng dụng sẽ chạy.

```bash
sha256sum backup.tar.gz
tar -tzf backup.tar.gz
```

`tar -t` liệt kê thành phần archive. Tiếp theo phải giải nén ở một **thư mục thử riêng** và kiểm tra file/permission/service.

Đọc lệnh `tar -czf backup.tar.gz -C /srv appdata`: `-c` tạo archive, `-z` nén gzip, `-f` chọn tên archive, `-C /srv` đổi working directory trước khi thêm `appdata`. Archive chứa path tương đối `appdata/...`, thuận tiện restore vào staging. `tar -tzf` chỉ xem danh sách, `tar -xzf backup.tar.gz -C /tmp/restore-test` mới giải nén. Trước khi chạy trên data thật, kiểm listing và destination; đừng restore một archive lạ thẳng vào `/`.

## Restore drill

1. Chọn backup và đối chiếu timestamp, checksum.
2. Tạo thư mục restore tách khỏi nguồn.
3. Liệt kê archive trước khi giải nén; chú ý absolute path và `../` trong archive lạ.
4. Restore dữ liệu vào vị trí thử.
5. So file hash, owner, mode, số lượng file.
6. Chạy ứng dụng hoặc kiểm tra logic đọc dữ liệu.
7. Ghi thời gian thực tế để so với RTO.

## Checksum chứng minh tới đâu

| Phép kiểm | Chứng minh | Không chứng minh |
|---|---|---|
| `sha256sum` archive khớp | Archive không đổi từ lúc tạo | Nội dung đầy đủ, nhất quán |
| `tar -tzf` | Archive đọc được, có danh sách file | Restore đúng owner/mode |
| Restore + `diff -r` + `stat` | Nội dung và metadata khớp source | Ứng dụng chạy được |
| App đọc được data restored | **Restore dùng được** | — |

## Tự kiểm tra

1. Hash archive khớp hôm tạo. Có chắc database trong đó dùng được không?
2. `rsync -a --delete /srv/app /backup/app/` khác `rsync -a --delete /srv/app/ /backup/app/` thế nào?
3. Vì sao restore vào staging thay vì thẳng vào vị trí thật?

<details>
<summary>Đáp án</summary>

1. Không — hash chỉ chứng minh archive không bị đổi; DB có thể crash-inconsistent. Phải restore và cho DB/app đọc thử.
2. Không có `/` cuối ở source → tạo `/backup/app/app/...`; có `/` → đồng bộ **nội dung** vào `/backup/app/`. Dùng `--dry-run` trước.
3. Để kiểm tra trước, không đè data đang dùng, và còn đường rollback.

</details>

## Nguồn

- [LPIC-2 Objective 206.2](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
