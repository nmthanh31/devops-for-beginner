# Bài 1 — FHS: tìm đúng config, data, log và command

> **LPIC-1 104.7:** làm quen FHS, nơi đặt file/thư mục thông dụng, và cách tìm file/lệnh. Nội dung bên dưới được giải thích lại để học, không chép nguyên văn giáo trình.

## FHS trả lời câu hỏi gì?

Filesystem Hierarchy Standard (FHS) đặt ra quy ước chung cho các đường dẫn trong Linux. Khi biết một file là cấu hình, log, dữ liệu ứng dụng hay command, ta có điểm bắt đầu hợp lý để tìm nó. Distro và package vẫn có thể khác nhau, nên hãy xác nhận trên máy thật thay vì đoán tuyệt đối.

| Đường dẫn | Vai trò thường gặp | Cách nhớ |
|---|---|---|
| `/etc` | cấu hình host-wide | cấu hình hệ thống |
| `/var/log` | log có thể thay đổi theo thời gian | log |
| `/var/lib` | state/data bền hơn của ứng dụng | dữ liệu vận hành |
| `/var/cache` | dữ liệu cache có thể tái tạo | cache |
| `/run` | runtime state tạm thời, thường mất khi reboot | trạng thái phiên boot hiện tại |
| `/usr/bin`, `/usr/sbin` | command do hệ thống/package cung cấp | chương trình đã cài |
| `/usr/share` | dữ liệu kiến trúc độc lập, thường chỉ đọc | tài liệu/asset dùng chung |
| `/opt` | phần mềm bổ sung bên thứ ba | ứng dụng cài riêng |
| `/home` | home của user thường | dữ liệu người dùng |
| `/root` | home của root | dữ liệu quản trị |
| `/tmp` | file tạm; có thể bị dọn | tạm thời |
| `/var/tmp` | file tạm có thể cần tồn tại lâu hơn `/tmp` | tạm nhưng giữ lâu hơn |
| `/srv` | dữ liệu được service cung cấp | dữ liệu phục vụ |
| `/proc`, `/sys`, `/dev` | giao diện pseudo-filesystem cho kernel/process/device | file-like interface, không phải kho file thông thường |

Đây là bản đồ học tập, không phải cam kết rằng mọi distro đều đặt từng file giống hệt nhau. Ví dụ log có thể nằm trong journal thay vì file log riêng; cấu hình của một ứng dụng phụ thuộc package.

## Tìm command: `type`, `command -v`, `which`, `whereis`

- `type -a name`: shell giải quyết tên đó ra sao; có thể cho thấy alias, function, builtin và executable.
- `command -v name`: hỏi shell tên command sẽ được phân giải thành gì.
- `which name`: thường tìm executable trong `PATH`; không phải lúc nào cũng phản ánh alias/function của shell.
- `whereis name`: tìm vị trí binary, source, man page theo cơ chế của công cụ; kết quả không nhất thiết liệt kê mọi bản cài.

Ví dụ:

~~~bash
type -a python3
command -v python3
whereis python3
~~~

## Tìm file: `find` và `locate`

`find` đi tìm trên filesystem hiện tại nên phản ánh trạng thái hiện có, nhưng có thể chậm và gặp permission denied. `locate` tra database đã tạo trước đó nên nhanh, nhưng database có thể cũ hoặc chưa được tạo. Trên nhiều máy, cập nhật database cần quyền quản trị; không cần chạy `updatedb` để hoàn thành lab.

~~~bash
find /etc -maxdepth 2 -type f -name '*ssh*' 2>/dev/null
find /var/log -maxdepth 2 -type f 2>/dev/null
locate sshd_config
~~~

`locate` không tìm được file mới không chứng minh file không tồn tại; dùng `find` để xác nhận.

## Nguồn

- [LPIC-1 Objectives V5.0 — 104.7](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [LPI Learning Material 101, Version 5.0 — lesson 104.7](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf)
- Phần pseudo-filesystems là mở rộng: [Linux kernel `/proc` documentation](https://docs.kernel.org/filesystems/proc.html), [Linux kernel `sysfs` documentation](https://docs.kernel.org/filesystems/sysfs.html)

