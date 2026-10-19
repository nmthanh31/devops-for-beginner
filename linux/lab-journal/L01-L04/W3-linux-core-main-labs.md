# W3 — Linux Core Main Labs (L01–L04)

**Tuần:** 12–18/10/2026  
**Phạm vi:** L01 Execution model · L02 Boot & service management · L03 Filesystem & path · L04 Identity & permissions  
**Mục đích:** hoàn thành lab thực hành chính trong tuần và tạo incident pack có thể dùng cho review/gate.  
**Không bao gồm:** bài giảng lý thuyết hoặc lời giải fault gate.

## Phạm vi an toàn

- Dùng VM lab an toàn. Máy `k8s-wk` hiện đã có `l04-lab-api.service` và `l04-catalog.service`; **không sửa, xóa, đổi port hoặc reboot máy để làm các bài dưới đây**.
- Nếu buộc phải dùng cùng VM, chọn tên user/unit/path/port hoàn toàn mới, chỉ bind loopback và không reboot.
- Không dùng `chmod 777`; không restart mù; mỗi lượt chỉ inject một fault.
- Trước cleanup, xác nhận chính xác target thuộc lab đang làm. Không xóa user/group nếu chưa kiểm tra chúng không được dùng nơi khác.
- Không đưa password, token hoặc secret vào file evidence.

## Bộ lab và thứ tự

| Buổi | Loại | Đầu ra |
|---|---|---|
| S2 | Guided Deploy | Service nhỏ chạy bằng service account, phục vụ HTTP, permission đúng |
| S3 | Operate/Break | Incident pack 4 lỗi L01–L04, có evidence trước/sau |
| S4 | Independent Build | Rebuild từ blank, README đủ để người khác tái lập |
| S5 | Gate/Review | 6 fault mù trong 90 phút, scorecard và kế hoạch D+7/D+30 |
| SX | Deepening, chỉ sau core PASS | FD→file/socket, open-unlinked, unit dependency/order |

Các bài đã làm trong tuần có thể được dùng làm evidence; không cần dựng lại phần đã đạt nếu còn đầy đủ bằng chứng. Phần chưa đạt thì repair và retest.

## S2 — Guided Deploy: systemd service dưới user riêng

### Đề bài

Trong VM lab, dựng một HTTP service nội bộ có tên/port riêng. Service phải chạy bằng user không đặc quyền, phục vụ một trang `index.html`, có working directory, environment, data path và log có thể tra cứu. Service chỉ bind loopback trong phần lab cốt lõi.

### Yêu cầu đầu ra

- [x] Service account riêng, không đăng nhập shell và không chạy service bằng root.
- [x] Unit systemd có command, `User`/`Group`, working directory, environment và restart policy.
- [x] `index.html` nằm trong data path riêng; owner/mode cấp vừa đủ để service đọc.
- [x] Service khởi động được; HTTP trả đúng nội dung.
- [x] Có positive test và negative test.
- [x] Log của lần khởi động và request được tìm thấy.

### Evidence

Lưu unit, service status, log, process PID/PPID/UID/GID/cwd/environment, file owner/mode, `namei` trên path, listener và HTTP response. Mỗi output cần một câu nói rõ nó chứng minh điều gì.

### DoD

Người khác có thể tái lập service theo README; bạn giải thích được từ unit tới process, file access, listener và HTTP response.

## S3 — Operate/Break: 4 lỗi có kiểm soát

Dùng bản lab riêng. Với từng lỗi: ghi dự đoán → inject đúng một cause → quan sát symptom → thu evidence → nêu root cause → sửa tối thiểu → verify positive và negative path → cleanup/restore.

### Bốn fault cần thực hành

1. **ExecStart:** làm service không chạy đúng command/executable.
2. **Environment hoặc cwd:** làm process nhận sai/mất environment cần thiết hoặc khởi chạy với working directory không hợp lệ.
3. **Port conflict:** làm port cần dùng bị một process lab khác chiếm.
4. **Parent-directory permission:** làm service không traverse/read được path cần phục vụ do quyền trên một thư mục cha.

Không đổi nhiều yếu tố cùng lúc. Không dùng restart để thay cho việc đọc trạng thái/log; restart chỉ dùng sau khi đã ghi evidence và sửa cause.

### Bảng incident

| # | Symptom/impact | Evidence trước sửa | Root cause | Sửa tối thiểu | Verify sau sửa | Cleanup/rollback |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |

### DoD

- [ ] Định vị đúng cả 4 lỗi trước khi sửa.
- [ ] Không dùng `777`, không sửa ngoài phạm vi lab.
- [ ] Lưu trạng thái/log/process/socket/path evidence trước và sau.
- [ ] Mỗi lần chỉ inject một cause và có cleanup/rollback.

## S4 — Independent Build: cold rebuild

### Đề bài

Tạo một service thứ hai từ blank, tách khỏi Guided Deploy. Trong 20 phút đầu không mở notes. Tự chọn tên riêng cho service account, unit, environment, data/log path và port; không sử dụng lại danh tính/path của hai service đang có trên `k8s-wk`.

Service cần có:

- [ ] Service account riêng và least privilege.
- [ ] Unit systemd do bạn tự viết.
- [ ] Environment configuration không chứa secret.
- [ ] Data path và log path (hoặc journal logging được ghi rõ trong README).
- [ ] Health endpoint trả response mong đợi.
- [ ] Listener đúng địa chỉ/port; positive và negative test.
- [ ] Quy trình stop/cleanup an toàn.

### README tái lập

README phải ghi prerequisite, resource names, lệnh/thao tác theo đúng thứ tự, kết quả mong đợi, cách verify, cách xử lý lỗi thường gặp và cleanup. Không chỉ dán output; cần diễn giải ngắn từng evidence.

### DoD

- [ ] Dựng lại được từ blank không phụ thuộc file/unit cũ.
- [ ] Service chạy bằng user đúng và HTTP/health hoạt động.
- [ ] Có bằng chứng quyền đọc/ghi và path traversal.
- [ ] Người khác có thể tái lập theo README.
- [ ] Có thể kiểm tra trạng thái enablement. Chỉ reboot để verify boot nếu đó là VM disposable và reboot được cho phép; nếu không, không reboot, ghi rõ giới hạn.

## S5 — Gate/Review: 6 fault mù

**Timebox:** 90 phút. Gate cần được đưa từng tình huống một; không xem root cause trước. Dùng một bản lab disposable, không inject lỗi lên unit đang dùng hoặc service của cluster. Đề fault không được ghi kèm lời giải trong file này.

Mỗi fault phải có:

1. Symptom và impact.
2. Hypothesis trước khi sửa.
3. Evidence từ ít nhất hai lớp liên quan.
4. Root cause.
5. Fix tối thiểu và rollback plan.
6. Positive/negative verification.

### Gate scorecard

| Fault | Root cause đúng? | Fix đúng? | Verify đầy đủ? | Evidence/ghi chú |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |

**PASS:** root cause đúng ít nhất 5/6; fix đúng ít nhất 4/6; evidence và verification đầy đủ. Nếu FAIL, tuần kế tiếp chỉ repair các domain đỏ, chưa mở nội dung nâng cao.

## SX — Deepening, chỉ khi core PASS

- [ ] Map process FD tới file/socket; chứng minh bằng evidence.
- [ ] Thực hành open-unlinked file trong thư mục lab tạm; chứng minh pathname đã mất nhưng process vẫn giữ FD, sau đó đóng process/FD và xác nhận giải phóng.
- [ ] Quan sát unit dependency/order trên các unit lab riêng; phân biệt dependency với thứ tự khởi động.
- [ ] Explain-back 5 phút không notes.

Nếu chưa đạt S2–S5, bỏ SX và dùng thời gian để repair.

## Evidence pack cuối tuần

- [ ] Diagram: unit → process → identity/env/cwd/FD → path/socket → HTTP.
- [ ] Unit và cấu hình đã sanitize.
- [ ] Process/`/proc` evidence.
- [ ] `stat`/`namei`/permission evidence.
- [ ] Journal, listener, curl positive/negative results.
- [ ] Bốn incident S3 đã có before/after.
- [ ] README independent rebuild.
- [ ] Gate scorecard; domain PASS/repair; D+7/D+30 review date.
- [ ] Cleanup record xác nhận chỉ tài nguyên lab bị dừng/xóa.

## Kết quả tuần

- S2 Guided Deploy: PASS / NEEDS REPAIR
- S3 Operate/Break: ____ / 4 fault đúng trước sửa
- S4 Independent Build: PASS / NEEDS REPAIR
- S5 Gate: ____ / 6 root cause đúng · ____ / 6 fix đúng
- Domain đỏ cần repair:
- D+7:
- D+30:
