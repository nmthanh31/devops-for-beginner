# Bài 3 — Runbook khôi phục và evidence

> **Sau bài này bạn sẽ:**
> - Viết runbook mà **người khác** chạy được không cần hỏi bạn.
> - Biết evidence nào cần lưu sau mỗi lần backup/restore.
> - Tránh 6 lỗi hay gặp nhất.
>
> **Cần trước:** [Bài 2](./02-consistency-and-restore.md).

## Runbook là gì?

Runbook là hướng dẫn đủ cụ thể để người khác thực hiện khôi phục: điều kiện bắt đầu, path, lệnh, kết quả dự kiến, bước kiểm tra và rollback. Runbook tốt không dựa vào trí nhớ của người tạo backup.

## Mẫu quy trình

```text
Incident: dữ liệu service mất hoặc sai
   ↓
xác định phạm vi và ngăn ghi thêm nếu cần
   ↓
kiểm tra mount/UUID và source backup
   ↓
chọn recovery point phù hợp RPO
   ↓
verify archive/checksum
   ↓
restore vào staging và kiểm tra
   ↓
đưa service dùng dữ liệu restored
   ↓
positive test + negative test + log
```

Nếu storage không mount mà service vẫn ghi vào thư mục mountpoint trên root filesystem, backup có thể lấy nhầm dữ liệu. Trước backup và sau restore, dùng `findmnt --mountpoint PATH` để xác minh nguồn thật.

## Evidence cần lưu

- path source và destination đã kiểm tra;
- thời điểm backup và kích thước;
- checksum archive;
- danh sách file/metadata cần thiết;
- hash hoặc test nội dung sau restore;
- service status và application response;
- thời gian restore và mọi sai lệch so với RTO/RPO.

Không lưu secret trong report. Nếu archive chứa secret, bảo vệ quyền đọc, mã hóa và vòng đời xóa theo chính sách lab.

## Lỗi hay gặp

- Backup thành công nhưng chưa từng restore thử.
- Copy dữ liệu vào cùng disk rồi tin rằng đã có offsite backup.
- Restore đè lên data đang dùng mà không có rollback.
- Database backup không nhất quán.
- Tạo archive từ path tương đối sai vì working directory thay đổi.
- `rsync --delete` trỏ nhầm destination.

## Mẫu runbook (copy và điền)

```markdown
# Runbook: restore <service>
- Điều kiện bắt đầu: <triệu chứng / quyết định của ai>
- Recovery point: <file archive>, tạo lúc <UTC>, sha256 <...>
- Source backup: <path / host>   · Đích: <path>   · Mount kiểm bằng: findmnt --mountpoint <path>
| Bước | Lệnh | Kết quả mong đợi | Nếu khác thì |
|---|---|---|---|
| 1 | systemctl stop <svc> | inactive | dừng, báo |
| 2 | sha256sum -c <hashfile> | OK | chọn bản khác |
| 3 | tar -tzf <archive> | không có path tuyệt đối/../ | dừng |
| 4 | tar -xzf <archive> -C <staging> | — | — |
| 5 | diff / stat / test app trên staging | khớp | dừng |
| 6 | chuyển staging → đích (giữ bản cũ để rollback) | — | rollback |
| 7 | systemctl start <svc>; curl health/readiness | 200 | rollback |
- Rollback: <lệnh>
- Thời gian thực tế: <phút> (RTO mục tiêu <phút>)
```

## Tự kiểm tra

Service ghi vào `/srv/data`, nhưng disk data quên mount sau reboot. Backup đêm đó "thành công". Điều gì đã xảy ra, và lệnh nào trong runbook phát hiện được?

<details>
<summary>Đáp án</summary>

Service ghi vào thư mục mountpoint trên root FS; backup chụp dữ liệu trống/sai, không phải disk data thật. `findmnt --mountpoint /srv/data` trước backup sẽ không trả về gì → dừng.

</details>

## Nguồn

- [LPIC-2 Objective 206.2](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
