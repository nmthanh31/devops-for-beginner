# Lab 1 — SIGTERM vs SIGKILL

## Mục tiêu

Quan sát sự khác nhau giữa:

- SIGTERM: process có thể nhận, xử lý và cleanup;
- SIGKILL: kernel terminate process, process không có cơ hội cleanup.

## Chuẩn bị

Cần có Linux shell, Python 3 và hai terminal.

## Bước 1: Tạo signal demo

~~~bash
mkdir -p /tmp/l01
nano /tmp/l01/signal-demo.py
~~~

Nội dung:

~~~python
import os
import signal
import sys
import time


def shutdown(signum, frame):
    print(f"Received signal: {signum}", flush=True)
    print("Cleaning up...", flush=True)
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown)

print(f"PID={os.getpid()}", flush=True)

while True:
    time.sleep(1)
~~~

## Bước 2: Chạy process

Terminal 1:

~~~bash
python3 -u /tmp/l01/signal-demo.py
~~~

Ghi lại PID được in ra.

## Bước 3: Gửi SIGTERM

Terminal 2:

~~~bash
kill -TERM <PID>
~~~

Hoặc:

~~~bash
kill <PID>
~~~

Kết quả mong đợi:

~~~text
Received signal: 15
Cleaning up...
~~~

Giải thích:

1. kill mặc định gửi SIGTERM.
2. Process nhận signal.
3. Signal handler được chạy.
4. Process thực hiện cleanup.
5. Process kết thúc với exit code 0 do sys.exit(0).

## Bước 4: Chạy lại process

~~~bash
python3 -u /tmp/l01/signal-demo.py
~~~

Ghi PID mới.

## Bước 5: Gửi SIGKILL

~~~bash
kill -9 <PID>
~~~

Lần này không thấy dòng:

~~~text
Cleaning up...
~~~

Giải thích:

1. -9 là SIGKILL.
2. Kernel terminate process trực tiếp.
3. Process không thể catch hoặc ignore SIGKILL.
4. Signal handler không được chạy.
5. Cleanup của application không được thực hiện.

## Bảng so sánh

| Đặc điểm | SIGTERM | SIGKILL |
|---|---|---|
| Số signal | 15 | 9 |
| Process có thể catch? | Có | Không |
| Có thể cleanup? | Có | Không |
| Có handler? | Có | Không |
| Nên dùng đầu tiên? | Có | Không |

## Câu hỏi kiểm tra

1. kill PID mặc định gửi signal nào?
2. Vì sao SIGTERM chạy được cleanup?
3. Vì sao SIGKILL không chạy cleanup?
4. Khi nào mới nên dùng SIGKILL?
5. Nếu process bắt SIGTERM rồi gọi sys.exit(0), exit code là bao nhiêu?

## Cleanup

~~~bash
rm -rf /tmp/l01
~~~

Chỉ xóa đúng thư mục test đã tạo cho lab này.

