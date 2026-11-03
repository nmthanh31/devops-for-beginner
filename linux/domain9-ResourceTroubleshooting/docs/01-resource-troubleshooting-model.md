# Bài 1 — Mô hình chẩn đoán tài nguyên

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Biến "máy chậm" thành câu hỏi đo được: CPU, memory hay I/O?
> - Đi từ rộng (host) → hẹp (process) → log, và luôn có **≥ 2 bằng chứng** trước khi kết luận.
> - Phân biệt utilization, saturation, errors (USE).
>
> **Hình dung:** bác sĩ không kê thuốc chỉ vì "mệt" — đo nhiệt độ, huyết áp, xét nghiệm rồi mới chẩn đoán. Restart service khi chưa đo giống uống thuốc hạ sốt cho bệnh chưa biết tên.


## “Máy chậm” chưa phải là nguyên nhân

“Máy chậm” chỉ là triệu chứng. Trước khi chạy lệnh, cần làm rõ:

1. Thành phần nào chậm: toàn máy, một service hay một request?
2. Chậm từ lúc nào, liên tục hay theo từng đợt?
3. Gần thời điểm đó có deploy, backup, cron, package update hoặc thay đổi traffic không?
4. Chỉ một người gặp hay mọi client đều gặp?

Nếu không xác định thời điểm và phạm vi, bạn rất dễ đo một trạng thái bình thường rồi gán nó cho sự cố đã xảy ra trước đó.

## Đi từ rộng đến hẹp

```text
host có thực sự chịu áp lực?
        ↓
áp lực thuộc CPU, memory hay I/O?
        ↓
process/cgroup nào liên quan?
        ↓
log và timeline có khớp không?
        ↓
thay đổi nhỏ nhất để kiểm chứng giả thuyết
```

Ví dụ, nếu API chậm:

- `uptime`, `vmstat` cho biết tình trạng chung của host.
- `top`, `ps` chỉ ra process đang dùng CPU hoặc memory.
- `iostat`, `iotop` kiểm tra storage và process tạo I/O.
- `journalctl` giúp nối số liệu với lỗi service hoặc kernel trong cùng thời điểm.

## Một metric không đủ để kết luận

Ví dụ:

- Load average cao không tự động có nghĩa là CPU quá tải.
- RAM `free` thấp không tự động có nghĩa là hết RAM.
- `%util` của disk cao không tự động chứng minh disk là nguyên nhân ứng dụng chậm.
- Một process dùng 100% CPU có thể chỉ đang dùng đầy một core và vẫn là hành vi bình thường.

Một kết luận tốt cần ít nhất hai lớp bằng chứng:

```text
host metric + process metric
host metric + kernel/service log
process metric + application symptom
```

## Quy trình evidence

Ghi lại theo mẫu:

```text
Question: API chậm có phải vì CPU saturation không?
Prediction: nếu đúng, CPU idle sẽ thấp, runnable queue cao và process API đứng đầu CPU.
Command: vmstat 1 10; ps ... --sort=-%cpu
Result: ghi đúng output quan trọng.
Decision: chấp nhận hoặc loại giả thuyết.
```

Restart có thể làm triệu chứng biến mất nhưng cũng xóa mất trạng thái cần điều tra. Hãy thu evidence trước khi restart nếu hệ thống vẫn an toàn.

<!-- learn:tail -->
## Tự kiểm tra

1. CPU 95% liên tục. Đã đủ kết luận CPU là bottleneck chưa?
2. Ba chữ trong USE?

<details>
<summary>Đáp án</summary>

1. Chưa — cần dấu hiệu **saturation** (run queue > số CPU, latency app tăng cùng lúc) và process gây ra.
2. Utilization, Saturation, Errors.

</details>

## Nguồn

- [LPIC-2 V4.5 — Objective 200.1](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
