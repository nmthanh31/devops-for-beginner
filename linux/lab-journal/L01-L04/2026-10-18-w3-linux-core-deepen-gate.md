# 2026-10-18 — W3 Linux Core: Deepen/Repair + Gate L01–L04

**Thời lượng theo lịch:** 09:00–11:00 Deepen/Repair; 20:30–22:00 Gate/Review  
**Phạm vi:** L01 Execution model · L02 systemd/service · L03 filesystem/path · L04 identity/permissions  
**Chế độ:** đề bài độc lập; không kèm lời giải hoặc danh sách nguyên nhân của fault gate

## Mục tiêu

Tự dựng lại một service nhỏ trong môi trường sạch, nối được unit → process → identity/environment/cwd → file path/log → listener → HTTP response; sau đó chứng minh khả năng chẩn đoán và sửa lỗi bằng evidence.

## Phạm vi an toàn

- Làm trong VM lab an toàn; không reboot máy hoặc ảnh hưởng workload cần giữ ổn định.
- Không sửa hoặc tái sử dụng unit/user/path hiện có của `l04-lab-api` hay `l04-catalog`.
- Dùng tên và port riêng cho bài mới. Gợi ý tên: `core-review.service`, user `coreapp`, port `18084`; trước khi dùng phải xác nhận chúng chưa tồn tại/đang được dùng.
- Bind loopback cho phần cốt lõi. Không mở ra interface mạng của VM trong bài này.
- Không dùng `chmod 777`; chỉ thay đổi một cause mỗi lượt; không reboot/restart mù.
- Không ghi password, token hoặc secret vào evidence.

## Block 1 — Deepen/Repair · 09:00–11:00

### 20 phút đầu — closed notes

Không mở tài liệu. Vẽ kiến trúc dự định và viết dự đoán:

- [ ] systemd sẽ khởi chạy process nào và dưới UID/GID nào?
- [ ] Unit lấy environment ở đâu; process có cwd nào?
- [ ] Config, data và log nằm ở đâu; ai sở hữu chúng?
- [ ] Process cần quyền gì trên mỗi thư mục và file?
- [ ] Listener ở địa chỉ/port nào; positive và negative HTTP test sẽ là gì?

### Bài dựng độc lập

Từ blank, dựng một HTTP service mới đáp ứng các điều kiện:

1. Chạy bằng user hệ thống riêng `coreapp`, không chạy bằng root.
2. Dùng environment configuration riêng, không chứa secret.
3. Có data directory riêng, trang chính `/` và health path `/health`; cả hai trả HTTP 200.
4. Có log path riêng, hoặc chọn journald và giải thích vì sao đó là log source của service.
5. systemd quản lý service; unit có working directory và restart policy phù hợp.
6. Listener chỉ bind `127.0.0.1` trên port đã chọn.
7. Service đọc được data cần phục vụ nhưng không có quyền ghi nếu chức năng chỉ cần đọc.
8. Có positive test và negative test; giải thích đúng điều mỗi test chứng minh.

Nếu điểm yếu từ lab trước còn chưa vững, ưu tiên repair điểm đó trước khi thêm phần mở rộng. Không mở chủ đề tuần kế tiếp.

### Evidence và DoD của block 1

Ghi command/output cần thiết và một câu giải thích cho mỗi nhóm evidence:

- [ ] Unit và cấu hình environment đã sanitize.
- [ ] `systemctl status` và log chứng minh trạng thái khởi động.
- [ ] PID/PPID, UID/GID, cwd, environment và FD/process context.
- [ ] Owner/mode trên file cùng từng parent directory.
- [ ] Listener address/port.
- [ ] HTTP response cho `/` và `/health`.
- [ ] Test quyền đọc và test quyền ghi dưới identity của service.
- [ ] Cleanup chỉ nhắm tới tài nguyên của bài mới.

**DoD:** tạo được evidence mới; nếu làm lại một check/fault đã từng sai, phải retest đạt ít nhất 80% các mục đã đặt ra.

## Block 2 — Gate/Review · 20:30–22:00

Thực hiện 6 fault mù trên một bản lab riêng. Nhận từng tình huống từ trainer khi bắt đầu; không ghi hoặc xem trước nguyên nhân. Không dùng `l04-lab-api` hay `l04-catalog` làm nơi inject fault.

Với từng fault, ghi theo thứ tự:

1. Symptom và impact.
2. Hypothesis trước khi sửa.
3. Evidence từ ít nhất hai lớp liên quan.
4. Root cause.
5. Thay đổi tối thiểu/rollback plan.
6. Positive và negative verification sau sửa.

### Scorecard

| Fault | Root cause đúng? | Fix đúng và tối thiểu? | Verify đủ? | Evidence/ghi chú |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |

**PASS gate:** tìm đúng root cause ít nhất **5/6**, sửa đúng ít nhất **4/6**, và verify đầy đủ. Nếu FAIL, tuần sau chỉ repair các domain đỏ; không tự nâng level theo thời gian đã ngồi học.

## Explain-back

Không notes, giải thích trong 3–5 phút:

1. Unit dẫn tới process và listener như thế nào?
2. Kernel dùng UID/GID và mode/ACL/path permissions để quyết định truy cập ra sao?
3. Vì sao `active (running)` chưa chứng minh HTTP hoạt động?
4. Evidence nào giúp phân biệt lỗi process, systemd, filesystem permission và socket/listener?

## Review và spaced repetition

- **D+1:** vẽ lại flow 5 phút không notes.
- **D+7:** làm một biến thể lỗi khác với bài gate.
- **D+30:** đưa một incident trộn domain vào bài review.

## Tổng kết buổi

- Domain đạt:
- Domain cần repair:
- Root cause thường đoán sai:
- Evidence quyết định nhất:
- Cleanup đã làm:
- D+7 / D+30:
