# L01 — Command Reference

> Cheat sheet command cho toàn bộ Buổi 1 — Linux Execution Model.

File này dùng để tra cứu nhanh. Phần giải thích lý thuyết nằm trong các file bài học riêng.

---

## 1. Shell và process hiện tại

PID của shell hiện tại:

~~~bash
echo $$
~~~

Tạo một process chạy nền:

~~~bash
sleep 300 &
~~~

PID của process nền gần nhất:

~~~bash
echo $!
~~~

Lưu PID vào biến để dùng tiếp:

~~~bash
PID=$!
echo "$PID"
~~~

Chờ process kết thúc:

~~~bash
wait "$PID"
~~~

---

## 2. Xem process bằng ps

Xem process theo PID:

~~~bash
ps -p "$PID"
~~~

Xem đầy đủ thông tin cơ bản:

~~~bash
ps -o pid,ppid,user,group,stat,state,cmd -p "$PID"
~~~

Xem UID/GID:

~~~bash
ps -o pid,user,group,uid,gid,cmd -p "$PID"
~~~

Xem command line đầy đủ:

~~~bash
ps -fp "$PID"
~~~

Xem toàn bộ process:

~~~bash
ps aux
~~~

Tìm process theo tên:

~~~bash
pgrep -a python
pgrep -a sleep
~~~

Ý nghĩa các cột quan trọng:

| Cột | Ý nghĩa |
|---|---|
| PID | Process ID |
| PPID | Parent Process ID |
| USER | User dạng tên |
| UID | User ID |
| GID | Group ID |
| STAT | Process state và flags |
| CMD | Command/process image |

---

## 3. Xem process tree

Cây bắt đầu từ shell hiện tại:

~~~bash
pstree -p $$
~~~

Cây của một PID:

~~~bash
pstree -p "$PID"
~~~

Cây toàn hệ thống:

~~~bash
pstree -p
~~~

Tìm parent trực tiếp bằng PPID:

~~~bash
ps -o pid,ppid,cmd -p "$PID"
~~~

---

## 4. Quan sát process qua /proc

Liệt kê các entry của process:

~~~bash
ls -la /proc/"$PID"
~~~

Xem command line:

~~~bash
cat /proc/"$PID"/cmdline
~~~

Đổi ký tự null thành khoảng trắng để dễ đọc:

~~~bash
tr '\0' ' ' < /proc/"$PID"/cmdline
echo
~~~

Xem status:

~~~bash
cat /proc/"$PID"/status
~~~

Chỉ xem PID, PPID, state, UID và GID:

~~~bash
grep -E '^(Name|State|Pid|PPid|Uid|Gid):' /proc/"$PID"/status
~~~

---

## 5. Kiểm tra executable và CWD

Executable process đang chạy:

~~~bash
readlink /proc/"$PID"/exe
~~~

Working directory của process:

~~~bash
readlink /proc/"$PID"/cwd
~~~

Working directory của shell hiện tại:

~~~bash
pwd
readlink /proc/$$/cwd
~~~

Đổi CWD của shell:

~~~bash
cd /tmp
readlink /proc/$$/cwd
~~~

Kiểm tra command line và executable cùng lúc:

~~~bash
ps -o pid,cmd -p "$PID"
readlink /proc/"$PID"/exe
~~~

---

## 6. Environment Variables

Xem toàn bộ environment của shell:

~~~bash
printenv
~~~

Xem một biến:

~~~bash
printenv APP_ENV
echo "$APP_ENV"
~~~

Tạo shell variable:

~~~bash
DEMO_LOCAL="local-value"
~~~

Export thành environment variable:

~~~bash
export DEMO_ENV="hello-linux"
~~~

Truyền biến cho một command duy nhất:

~~~bash
DEMO_TEMP="only-this-command" printenv DEMO_TEMP
~~~

Tạo child shell để kiểm tra inheritance:

~~~bash
bash
echo "$DEMO_ENV"
exit
~~~

Xem environment runtime của process:

~~~bash
tr '\0' '\n' < /proc/"$PID"/environ
~~~

Tìm một biến trong process:

~~~bash
tr '\0' '\n' < /proc/"$PID"/environ | grep '^APP_ENV='
~~~

Xóa biến:

~~~bash
unset DEMO_ENV
~~~

---

## 7. UID/GID của process

Xem UID/GID bằng ps:

~~~bash
ps -o pid,user,group,uid,gid,cmd -p "$PID"
~~~

Xem UID/GID trong /proc:

~~~bash
grep -E '^(Uid|Gid):' /proc/"$PID"/status
~~~

Xem user hiện tại:

~~~bash
id
~~~

Xem user name, UID, group và GID:

~~~bash
id -un
id -u
id -gn
id -g
~~~

Không dùng user terminal hiện tại để suy đoán user của process. Hãy kiểm tra đúng PID.

---

## 8. File Descriptor

Liệt kê FD của shell hiện tại:

~~~bash
ls -l /proc/$$/fd
~~~

Liệt kê FD của process khác:

~~~bash
ls -l /proc/"$PID"/fd
~~~

Xem FD 0, 1 và 2:

~~~bash
readlink /proc/$$/fd/0
readlink /proc/$$/fd/1
readlink /proc/$$/fd/2
~~~

Tạo file mẫu:

~~~bash
printf 'hello-linux\n' > /tmp/l01-demo.txt
~~~

Mở file bằng FD 3:

~~~bash
exec 3</tmp/l01-demo.txt
~~~

Kiểm tra FD 3:

~~~bash
readlink /proc/$$/fd/3
~~~

Đọc file thông qua FD 3:

~~~bash
cat <&3
~~~

Đóng FD 3:

~~~bash
exec 3<&-
~~~

Xem resource mà process đang giữ:

~~~bash
lsof -p "$PID"
~~~

Xem resource của shell:

~~~bash
lsof -p $$
~~~

---

## 9. Process và TCP socket

Khởi động HTTP server nền:

~~~bash
python3 -m http.server 8080 >/tmp/l01-http.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID"
~~~

Kiểm tra process:

~~~bash
ps -fp "$SERVER_PID"
~~~

Kiểm tra process có đang LISTEN không:

~~~bash
ss -lntp
~~~

Lọc port 8080:

~~~bash
ss -lntp | grep ':8080'
~~~

Mapping process với socket:

~~~bash
lsof -Pan -p "$SERVER_PID" -i
~~~

Xem toàn bộ FD của server:

~~~bash
lsof -p "$SERVER_PID"
~~~

Kiểm tra HTTP response:

~~~bash
curl -I http://127.0.0.1:8080
~~~

Dừng server sau khi kiểm tra:

~~~bash
kill "$SERVER_PID"
wait "$SERVER_PID"
~~~

---

## 10. Thread

Liệt kê thread directory:

~~~bash
ls -la /proc/"$PID"/task
~~~

Xem thread bằng ps:

~~~bash
ps -T -p "$PID"
~~~

Xem thread với nhiều cột hơn:

~~~bash
ps -o pid,ppid,tid,lwp,stat,comm -T -p "$PID"
~~~

Mỗi directory bên trong /proc/PID/task thường tương ứng với một thread ID.

---

## 11. Process state

Xem state của process:

~~~bash
ps -o pid,ppid,state,stat,cmd -p "$PID"
~~~

Xem state trong /proc:

~~~bash
grep -E '^(State|Pid|PPid):' /proc/"$PID"/status
~~~

Các state cơ bản:

| State | Ý nghĩa |
|---|---|
| R | Running hoặc runnable |
| S | Interruptible sleep |
| D | Uninterruptible sleep |
| T | Stopped |
| Z | Zombie |

Tạo process sleeping để quan sát:

~~~bash
sleep 1000 &
SLEEP_PID=$!
ps -o pid,ppid,state,stat,cmd -p "$SLEEP_PID"
~~~

Dọn process:

~~~bash
kill "$SLEEP_PID"
wait "$SLEEP_PID"
~~~

---

## 12. Signal

Kiểm tra process có tồn tại và có thể nhận signal không:

~~~bash
kill -0 "$PID"
~~~

Gửi SIGTERM:

~~~bash
kill -TERM "$PID"
~~~

Hoặc:

~~~bash
kill "$PID"
~~~

Gửi SIGKILL:

~~~bash
kill -KILL "$PID"
~~~

Hoặc:

~~~bash
kill -9 "$PID"
~~~

Gửi SIGINT:

~~~bash
kill -INT "$PID"
~~~

Gửi SIGHUP:

~~~bash
kill -HUP "$PID"
~~~

Xác nhận process đã kết thúc:

~~~bash
ps -p "$PID"
kill -0 "$PID"
~~~

Thứ tự nên dùng:

~~~text
SIGTERM → chờ cleanup → kiểm tra lại → SIGKILL nếu cần
~~~

---

## 13. Exit code

Command thành công:

~~~bash
true
echo $?
~~~

Command thất bại:

~~~bash
false
echo $?
~~~

Kiểm tra kết quả grep:

~~~bash
grep root /etc/passwd
echo $?

grep this-user-does-not-exist /etc/passwd
echo $?
~~~

Đọc exit code của process nền:

~~~bash
false &
PID=$!
wait "$PID"
echo $?
~~~

Nếu command cuối cùng là wait, shell sẽ quan sát exit status của process được wait.

---

## 14. Independent lab: HTTP server port 9090

Chạy server với CWD và environment cụ thể:

~~~bash
cd /tmp
APP_ENV=production python3 -m http.server 9090 >/tmp/l01-9090.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID"
~~~

Process:

~~~bash
ps -o pid,ppid,user,group,uid,gid,state,stat,cmd -p "$SERVER_PID"
~~~

Parent relationship:

~~~bash
pstree -p "$SERVER_PID"
ps -o pid,ppid,cmd -p "$SERVER_PID"
~~~

Executable:

~~~bash
readlink /proc/"$SERVER_PID"/exe
~~~

CWD:

~~~bash
readlink /proc/"$SERVER_PID"/cwd
~~~

Environment:

~~~bash
tr '\0' '\n' < /proc/"$SERVER_PID"/environ | grep '^APP_ENV='
~~~

Status:

~~~bash
grep -E '^(Name|State|Pid|PPid|Uid|Gid):' /proc/"$SERVER_PID"/status
~~~

FD:

~~~bash
ls -l /proc/"$SERVER_PID"/fd
lsof -p "$SERVER_PID"
~~~

Socket và listener:

~~~bash
ss -lntp | grep ':9090'
lsof -Pan -p "$SERVER_PID" -i
~~~

Kiểm tra server:

~~~bash
curl -I http://127.0.0.1:9090
~~~

Dừng bằng SIGTERM:

~~~bash
kill -TERM "$SERVER_PID"
wait "$SERVER_PID"
echo $?
~~~

Xem log:

~~~bash
cat /tmp/l01-9090.log
~~~

---

## 15. Cleanup thường dùng

Tìm process test:

~~~bash
pgrep -a -f 'http.server'
~~~

Dừng một process cụ thể:

~~~bash
kill -TERM "$PID"
~~~

Nếu process không dừng:

~~~bash
kill -KILL "$PID"
~~~

Xóa file test:

~~~bash
rm -f /tmp/l01-demo.txt /tmp/l01-http.log /tmp/l01-9090.log
~~~

Chỉ xóa đúng các file test đã tạo trong lab.

