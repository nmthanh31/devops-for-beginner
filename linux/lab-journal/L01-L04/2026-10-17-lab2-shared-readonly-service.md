# Lab 2 — Shared read-only content cho service

**Domain:** L01–L04 · Execution model, systemd, filesystem/path, identity & permissions  
**Chế độ:** tự làm từ đầu đến cuối — đề bài không kèm lời giải lệnh  
**Môi trường:** VM lab; không reboot máy hoặc sửa service/workload ngoài phạm vi bài

## Tình huống

Một service catalog cần phục vụ trang HTML. Tài khoản chạy service không sở hữu nội dung và chỉ được **đọc**, không được sửa. Nội dung do một nhóm quản lý riêng.

## Mục tiêu học tập

- Phân biệt owner, primary group và supplementary group của process.
- Tạo shared content theo least privilege.
- Nối systemd unit với process identity, cwd, file path và TCP listener.
- Chẩn đoán permission qua bằng chứng, không dùng `chmod 777`.
- Chứng minh service có thể đọc nội dung nhưng không thể ghi vào đó.

## Yêu cầu

1. Tạo service account `catalogsvc` và group chia sẻ `catalog-readers`.
2. Tạo trang `index.html` trong `/srv/l04-catalog/www/`.
3. Nội dung thuộc `root` và group `catalog-readers`; service đọc được file nhưng không ghi được.
4. Tạo systemd unit tên `l04-catalog.service`, chạy bằng `catalogsvc` và phục vụ trang tại `127.0.0.1:18083`.
5. Dùng systemd quản lý service; process không chạy bằng root.
6. Quyền trên từng thư mục cha phải cho phép service traverse tới trang; không mở quyền rộng hơn yêu cầu.
7. Không reboot VM. Chỉ tạo/sửa user, group, unit, port và đường dẫn dành riêng cho bài này.

Bạn tự chọn command, cách tạo file và cấu hình unit. Ghi lại dự đoán trước khi chạy lệnh quan trọng.

## Phần break/fix

Sau khi baseline chạy được, hãy tạo rồi sửa **hai lỗi riêng biệt**. Mỗi lần chỉ đưa vào một lỗi, giữ lại bằng chứng trước khi sửa và không làm ảnh hưởng tài nguyên ngoài lab.

### Fault A — Service chạy nhưng không phục vụ được trang

Tạo một lỗi liên quan đến quyền hoặc group khiến process không đọc được nội dung. Thu thập bằng chứng để phân biệt vấn đề identity/group với vấn đề owner/mode/path traversal; sau đó sửa bằng thay đổi tối thiểu.

### Fault B — systemd không khởi chạy service

Tạo một lỗi an toàn trong cấu hình unit hoặc đường dẫn cần thiết để service không khởi chạy đúng. Dùng trạng thái unit và journal để xác định nguyên nhân, sửa và xác minh lại.

**Quy tắc:** không tạo đồng thời nhiều lỗi; không dùng `chmod 777`; không sửa file của service khác; không dùng reboot làm cách chẩn đoán.

## Test matrix cần tự hoàn thành

| Kiểm tra | Dự đoán trước khi chạy | Kết quả thực tế | Bằng chứng / diễn giải |
|---|---|---|---|
| Service state sau khi start| | | |
| PID, PPID, UID/GID của process | | | |
| CWD và command của process | | | |
| Listener trên `127.0.0.1:18083` | | | |
| HTTP response và nội dung trang | | | |
| `catalogsvc` đọc được file | | | |
| `catalogsvc` không ghi được file | | | |
| Owner, group, mode và từng parent path | | | |
| Fault A: trước/sau sửa | | | |
| Fault B: trước/sau sửa | | | |

## Bằng chứng tối thiểu

Ghi lại command/output liên quan và giải thích điều output chứng minh:

- User/group database và identity thực tế của process.
- Unit file, `systemctl status` và journal trước/sau break/fix.
- PID/PPID, UID/GID, cwd và command line của process.
- Listener address/port và HTTP response.
- Owner/mode của file và thư mục; quyền traverse trên toàn bộ path.
- Kết quả phép thử đọc và ghi dưới identity `catalogsvc`.
- Với từng fault: triệu chứng, giả thuyết, bằng chứng, nguyên nhân, sửa tối thiểu và verify.

Che hoặc bỏ mọi thông tin nhạy cảm trước khi lưu output.

## Definition of Done

- [ ] Service hoạt động tại `http://127.0.0.1:18083/`.
- [ ] Process chạy dưới `catalogsvc`, không phải root.
- [ ] Service đọc được `index.html` nhưng không ghi được.
- [ ] Giải thích được vai trò của shared group và permission trên từng thành phần path.
- [ ] Hai fault được chẩn đoán và sửa bằng evidence.
- [ ] Không dùng `chmod 777`, reboot hoặc restart mù để thay cho diagnosis.
- [ ] Ghi cleanup và xác nhận chỉ tác động tài nguyên riêng của lab.
- [ ] Một người khác có thể hiểu và tái lập lab từ ghi chép của bạn.

## Troubleshooting log

| Fault | Triệu chứng | Bằng chứng trước sửa | Nguyên nhân | Sửa tối thiểu | Verify sau sửa |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |

## Cleanup

Ghi những gì đã stop, disable hoặc xóa. Trước khi xóa, xác nhận chính xác unit, user/group và các path thuộc bài lab; không xóa account nếu có tài nguyên khác đang sử dụng.

## Explain-back

Trả lời bằng lời của mình, không chỉ đọc output:

1. Process nhận group nào, và bằng chứng nào xác nhận điều đó?
2. Vì sao quyền đọc file chưa đủ nếu thiếu `x` trên một thư mục cha?
3. Vì sao process có thể đọc content mà không được phép sửa nó?
4. `active (running)` chứng minh điều gì và chưa chứng minh điều gì?
5. Với từng fault, bằng chứng nào giúp bạn phân biệt nguyên nhân thay vì đoán?

## Review

- Phần tự làm được không cần tra cứu:
- Phần phải tra cứu:
- Lỗi nào mất thời gian chẩn đoán nhất, và bằng chứng quyết định là gì:
- Một điều cần nhớ cho lab kế tiếp:
