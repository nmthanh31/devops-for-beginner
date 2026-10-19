# Lab 3 — Open-unlinked và dung lượng file

## Mục tiêu

Quan sát một process tiếp tục giữ file mở sau khi tên file bị xóa. Đây là nội dung nâng cao để hiểu khác biệt giữa namespace (tên/path) và object đang được process tham chiếu.

## Cảnh báo

Lab tạo một file riêng trong thư mục tạm và một process Python do chính bạn khởi chạy. Không thay tên file/path trong lệnh bằng file thật của ứng dụng. Cuối bài phải dừng đúng PID lab.

Chạy tuần tự các bước trong **cùng một terminal**, vì `LAB_DIR`, `LAB_FILE` và `LAB_PID` là biến của shell hiện tại.

## Bước 1 — Tạo file và process giữ file mở

~~~bash
LAB_DIR=$(mktemp -d /tmp/l03-open-unlinked.XXXXXX)
export LAB_FILE="$LAB_DIR/held.log"
python3 -c 'import os,time; f=open(os.environ["LAB_FILE"], "w"); f.write("held open by this process\n"); f.flush(); print("PID=", os.getpid(), flush=True); time.sleep(600)' &
LAB_PID=$!
echo "LAB_PID=$LAB_PID"
~~~

File descriptor vẫn mở vì biến `f` được giữ trong process Python đang ngủ.

## Bước 2 — Xác nhận process đang mở file

~~~bash
ps -o pid,ppid,stat,cmd -p "$LAB_PID"
lsof -p "$LAB_PID" | grep 'held.log'
~~~

Nếu máy không cài `lsof`, kiểm tra danh sách FD trực tiếp:

~~~bash
ls -l "/proc/$LAB_PID/fd"
~~~

## Bước 3 — Unlink path nhưng giữ process sống

~~~bash
rm "$LAB_FILE"
test ! -e "$LAB_FILE" && echo 'Path is gone'
ls -l "/proc/$LAB_PID/fd"
lsof -p "$LAB_PID" +L1
~~~

Path đã mất khỏi directory, nhưng FD trong `/proc/$LAB_PID/fd`/`lsof` còn tham chiếu object (thường hiển thị `(deleted)`). Giải thích vì sao dữ liệu chưa được giải phóng.

## Bước 4 — Đóng FD bằng cách dừng process

~~~bash
kill -TERM "$LAB_PID"
wait "$LAB_PID" 2>/dev/null || true
lsof +L1 2>/dev/null | grep 'l03-open-unlinked' || echo 'No lab file remains open'
rmdir "$LAB_DIR"
~~~

Khi process thoát, kernel đóng FD. Vì path đã unlink và không còn reference mở, filesystem có thể thu hồi object và dung lượng.

## Câu hỏi

1. `rm` xóa tên trong directory hay lập tức phá hủy mọi reference tới inode?
2. Vì sao `du` và `df` đôi khi cho cảm giác mâu thuẫn trong tình huống log deleted-but-open?
3. Trong sự cố thật, vì sao không nên kill process ngay khi `lsof +L1` tìm thấy file?

