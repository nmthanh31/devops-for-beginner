# Bài 1 — Backup bảo vệ điều gì và bảo vệ tới đâu?

> **Sau bài này bạn sẽ:**
> - Phân loại dữ liệu của một service (code / config / state / secret / log) và biết loại nào phải backup.
> - Phân biệt full / incremental / differential, RPO / RTO, backup / snapshot.
> - Chọn nơi lưu bản sao theo **failure domain**.
>
> **Cần trước:** [L05 Storage & mounts](../../domain5-Storage&Mounts/docs/README.md).

## Hình dung

Backup giống chìa khóa dự phòng. Để chìa dự phòng **trong cùng chùm** với chìa chính thì mất chùm là mất cả hai — đó là failure domain. Và chìa dự phòng chưa từng thử mở cửa thì chưa chắc dùng được — đó là restore drill.

## Backup là gì?

Backup là bản sao dữ liệu được giữ để phục hồi sau khi nguồn chính mất, hỏng, bị sửa nhầm hoặc không còn dùng được. **Restore** là thao tác đưa dữ liệu từ backup trở lại một môi trường sử dụng được.

`cp` sang một thư mục khác trên cùng filesystem có thể giúp khôi phục lỗi xóa nhầm, nhưng không bảo vệ trước hỏng disk. Bản sao phải nằm ở một failure domain phù hợp với rủi ro muốn chống.

## Xác định dữ liệu cần bảo vệ

| Loại | Ví dụ path | Cách tái tạo | Cần backup? |
|---|---|---|---|
| **Code/package** | `/usr/bin/app`, `/opt/app` | Cài lại từ artifact/repository | Thường không (giữ artifact + version) |
| **Configuration** | `/etc/app/`, unit file | Từ Git/IaC nếu có | **Có** (hoặc có trong Git) |
| **State/data** | `/srv/app/data`, database | **Không tái tạo được** | **Có — quan trọng nhất** |
| **Secret/key** | `/etc/app/secret.env`, TLS key | Cấp lại từ secret store | Có, nhưng mã hóa, quyền chặt, không vào repo công khai |
| **Log** | `/var/log/app` | — | Tùy yêu cầu audit; không cần để service chạy |

Viết danh sách path và cách tái tạo từng loại trước khi chọn lệnh backup.

## Full, incremental và differential

```text
CN   T2   T3   T4
Full  +Δ1  +Δ2  +Δ3     Incremental: Δ so với bản GẦN NHẤT → restore T4 = Full + Δ1 + Δ2 + Δ3
Full  +Δ   +Δ   +Δ      Differential: Δ so với FULL       → restore T4 = Full + Diff(T4)
```

| | Dung lượng / thời gian backup | Độ phức tạp restore |
|---|---|---|
| **Full** | Lớn nhất | Đơn giản nhất (1 bản) |
| **Incremental** | Nhỏ nhất | Cần cả chuỗi — mất một mắt xích là hỏng |
| **Differential** | Tăng dần tới lần full kế | Full + 1 bản |

Tradeoff chính là thời gian/dung lượng backup và độ phức tạp khi restore. Cần có retention policy: giữ bao nhiêu bản, trong bao lâu và khi nào kiểm tra được chúng.

## RPO và RTO

- **RPO (Recovery Point Objective):** mức mất dữ liệu tối đa chấp nhận được tính theo thời gian. RPO 1 giờ nghĩa là cần khả năng phục hồi về trạng thái không cũ quá khoảng 1 giờ.
- **RTO (Recovery Time Objective):** thời gian tối đa chấp nhận để service hoạt động trở lại.

RPO quyết định tần suất/sự nhất quán của backup. RTO ảnh hưởng cách chuẩn bị restore, vị trí backup và mức tự động hóa.

```text
10:00 backup ─────────── 10:40 incident ─────────── 11:10 service chạy lại
        ◄──── dữ liệu mất: 40′ (RPO thực tế) ────►◄──── downtime: 30′ (RTO thực tế) ────►
```

Ví dụ service tạo đơn hàng mỗi phút. Backup lúc 10:00, incident lúc 10:40 và restore bản 10:00: **mất tối đa 40 phút dữ liệu** trong tình huống đó (RPO thực tế), dù lệnh restore chỉ chạy 5 phút. Nếu service chỉ hoạt động lại lúc 11:10, thời gian khôi phục từ incident là **30 phút** (RTO thực tế). Hai con số đo hai điều khác nhau. Viết mục tiêu trước, sau đó làm drill để đo thực tế; tên file `backup-latest` không chứng minh đáp ứng RPO.

## Backup khác snapshot

Snapshot ghi lại trạng thái của volume/filesystem tại một thời điểm và hữu ích để tạo điểm đọc ổn định. Nếu snapshot nằm trên cùng storage và storage đó mất, snapshot cũng mất. Vì vậy snapshot có thể hỗ trợ quy trình backup nhưng không tự thay thế bản sao độc lập.

Failure domain là phạm vi một sự cố có thể làm mất cùng lúc nguồn và bản sao: cùng filesystem, cùng disk, cùng VM, cùng storage backend hoặc cùng vùng cloud. Bản `tar` để cạnh source trên cùng VM giúp chữa xóa nhầm file, nhưng không chữa hỏng VM/disk. Khi chọn nơi lưu, hỏi “sự cố nào cần chịu được?” rồi kiểm rằng ít nhất một bản sao nằm ngoài phạm vi sự cố đó.

| Bản sao nằm ở | Chống được | Không chống được |
|---|---|---|
| Thư mục khác, cùng filesystem | Xóa/sửa nhầm file | Hỏng FS, disk, VM |
| Disk khác, cùng VM | Hỏng một disk | Mất VM, ransomware trên VM |
| VM/host khác | Mất VM | Sự cố cả datacenter |
| Offsite / vùng cloud khác | Hầu hết sự cố cục bộ | (gần như đủ — nếu đã test restore) |

Quy tắc phổ biến **3-2-1**: 3 bản, 2 loại media, 1 bản offsite.

## Hiểu lầm thường gặp

| Hiểu lầm | Sự thật |
|---|---|
| "Có snapshot là có backup." | Snapshot cùng storage mất cùng storage. |
| "File `backup-latest` tồn tại là đạt RPO." | Phải kiểm timestamp và đã restore thử. |
| "RPO và RTO là một." | RPO = mất bao nhiêu dữ liệu; RTO = dừng bao lâu. |

## Tự kiểm tra

1. Backup mỗi 6h (00, 06, 12, 18). Incident lúc 17:30. RPO thực tế tối đa?
2. Incremental hằng ngày, full Chủ nhật. Bản Thứ Ba hỏng. Restore được Thứ Năm không?
3. `tar` để ở `/srv/backup` cùng disk với `/srv/app`. Chống được sự cố nào?

<details>
<summary>Đáp án</summary>

1. 5h30 (từ 12:00 tới 17:30).
2. Không — chuỗi incremental đứt ở Thứ Ba; chỉ restore được tới Thứ Hai.
3. Chỉ xóa/sửa nhầm file; không chống hỏng disk/VM.

</details>

## Nguồn

- [LPIC-2 Objective 206.2](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
