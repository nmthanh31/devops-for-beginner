# L08-02 — Controlled fault và repair

## Mục tiêu

Tạo một lỗi có kiểm soát trong script của L08-01, chẩn đoán bằng evidence rồi sửa đúng nguyên nhân.

## Chuẩn bị

```bash
cp -- safe-report.sh safe-report-fault.sh
```

Chỉ inject một fault trong mỗi lượt. Chọn một:

1. Bỏ quote ở một biến chứa path có khoảng trắng.
2. Đổi output directory thành path không tồn tại.
3. Xóa kiểm tra input directory.
4. Làm script không propagate lỗi của pipeline.

## Quy trình

1. Dự đoán symptom.
2. Chạy test với dữ liệu lab.
3. Thu stdout/stderr và exit code.
4. Xác định root cause.
5. Sửa tối thiểu một nguyên nhân.
6. Chạy lại positive và negative test.
7. Khôi phục bản script sạch.

## Bảng evidence

| Fault | Symptom | Evidence | Root cause | Fix | Retest |
|---|---|---|---|---|---|
| | | | | | |

## DoD

- [ ] Không sửa nhiều fault cùng lúc.
- [ ] Phân biệt symptom và root cause.
- [ ] Có positive/negative test sau sửa.
- [ ] Bản script sạch được khôi phục.
