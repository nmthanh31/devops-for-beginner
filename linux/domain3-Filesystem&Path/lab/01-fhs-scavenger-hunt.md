# Lab 1 — FHS scavenger hunt: tìm config, data, log

## Mục tiêu

Tập tìm file thật trên máy thay vì đoán vị trí; phân loại config, data, log, runtime state và executable theo FHS. Đây là phần thực hành của LPIC-1 104.7.

## Quy tắc

Chỉ đọc. Không sửa/xóa file trong `/etc`, `/var`, `/usr` hoặc thư mục hệ thống. Một số file/package có thể không tồn tại trên distro của bạn; hãy ghi nhận thay vì cài thêm package.

## Bước 1 — Tìm thông tin hệ thống

~~~bash
cat /etc/os-release
stat /etc/os-release
~~~

Ghi: đây là loại file gì, vì sao `/etc` là vị trí hợp lý?

## Bước 2 — Tìm command và xem cách shell phân giải

~~~bash
type -a bash
command -v bash
whereis bash
~~~

Ghi đường dẫn executable tìm được và giải thích vì sao output của ba lệnh có thể khác nhau.

## Bước 3 — Tìm cấu hình và log

~~~bash
find /etc -maxdepth 2 -type f -name '*ssh*' 2>/dev/null
find /var/log -maxdepth 2 -type f 2>/dev/null | head -n 20
~~~

Nếu SSH config không có trên máy, chọn một config thực tế dưới `/etc` thay thế. Với log, ghi nhận nếu distro của bạn chủ yếu dùng journal và không có nhiều file log thường.

## Bước 4 — Tìm application state và runtime state

~~~bash
find /var/lib -mindepth 1 -maxdepth 2 -type d 2>/dev/null | head -n 20
find /run -mindepth 1 -maxdepth 2 -type d 2>/dev/null | head -n 20
~~~

Chọn một ví dụ từ mỗi cây và phân loại: dữ liệu/state bền hơn hay runtime state tạm của lần boot hiện tại?

## Bước 5 — Hoàn thành bảng

| Vai trò | File/thư mục tìm được | Lệnh đã dùng | Lý do vị trí phù hợp |
|---|---|---|---|
| Config | | | |
| Data/state | | | |
| Log | | | |
| Runtime state | | | |
| Executable | | | |

## Câu hỏi

1. Vì sao không nên giả định mọi distro đều lưu log trong cùng một file?
2. Nếu `locate` không thấy một file vừa được tạo, điều đó chứng minh điều gì? (Gợi ý: database có thể cũ.)
3. Khi đã biết tên file nhưng chưa biết thư mục, khi nào `find` hữu ích hơn `which`?

