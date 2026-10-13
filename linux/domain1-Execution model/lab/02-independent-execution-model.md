# Lab 2 — Independent Execution Model

Đây là bài lab tổng hợp và là pass gate chính của Buổi 1.

## Mục tiêu

Dựng một HTTP server rồi dùng evidence để trả lời:

- process chạy program nào;
- PID và PPID là gì;
- process chạy dưới UID/GID nào;
- CWD là gì;
- environment có gì;
- process có FD nào;
- FD nào liên quan đến socket;
- listener bind ở đâu;
- process ở state nào;
- SIGTERM làm gì;
- exit status được quan sát thế nào.

## Quy tắc

Không chạy command kiểm tra ngay sau khi khởi động process.

Trước tiên phải viết prediction của bạn.

## Bước 1: Prediction

~~~text
1. Executable của process là gì?
2. PID của process là gì?
3. PPID là process nào?
4. UID/GID là gì?
5. CWD là gì?
6. APP_ENV có nằm trong environment không?
7. Process có những FD nào?
8. FD nào liên quan đến socket?
9. Listener bind ở địa chỉ nào?
10. Process state là gì?
11. Gửi SIGTERM thì chuyện gì xảy ra?
12. Shell quan sát exit status như thế nào?
~~~

## Bước 2: Khởi động process

~~~bash
cd /tmp
APP_ENV=production python3 -m http.server 9090 >/tmp/l01-9090.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID"
~~~

Lưu lại PID trong biến SERVER_PID.

## Bước 3: Kiểm tra process identity

~~~bash
ps -o pid,ppid,user,group,uid,gid,state,stat,cmd -p "$SERVER_PID"
~~~

Cần đọc được PID, PPID, user/group, UID/GID, state và command.

## Bước 4: Kiểm tra process tree

~~~bash
pstree -p "$$"
pstree -p "$SERVER_PID"
~~~

Mục tiêu là xác định server nằm dưới process nào.

## Bước 5: Kiểm tra executable và CWD

~~~bash
readlink /proc/"$SERVER_PID"/exe
readlink /proc/"$SERVER_PID"/cwd
~~~

CWD dự kiến là /tmp vì server được khởi động sau khi cd /tmp.

## Bước 6: Kiểm tra environment và status

~~~bash
tr '\0' '\n' < /proc/"$SERVER_PID"/environ | grep '^APP_ENV='
grep -E '^(Name|State|Pid|PPid|Uid|Gid):' /proc/"$SERVER_PID"/status
~~~

Environment dự kiến:

~~~text
APP_ENV=production
~~~

## Bước 7: Kiểm tra FD và socket

~~~bash
ls -l /proc/"$SERVER_PID"/fd
lsof -p "$SERVER_PID"
lsof -Pan -p "$SERVER_PID" -i
~~~

Xây dựng chain:

~~~text
python executable
      ↓
process PID
      ↓
FD
      ↓
socket
      ↓
TCP LISTEN
      ↓
:9090
~~~

## Bước 8: Kiểm tra TCP listener

~~~bash
ss -lntp | grep ':9090'
curl -I http://127.0.0.1:9090
~~~

## Bước 9: Gửi SIGTERM và đọc exit status

~~~bash
kill -TERM "$SERVER_PID"
wait "$SERVER_PID"
RESULT=$?
echo "$RESULT"
~~~

Kiểm tra process đã kết thúc:

~~~bash
ps -p "$SERVER_PID"
~~~

Xem log:

~~~bash
cat /tmp/l01-9090.log
~~~

## Evidence cần nộp

~~~text
PROCESS
PID:
PPID:
UID/GID:
STATE:

PROGRAM
exe:

RUNTIME CONTEXT
cwd:
environment:

RESOURCES
FD 0:
FD 1:
FD 2:
other FD:
socket:

NETWORK
listener:

RELATIONSHIP
parent:
children:

TERMINATION
signal used:
result:
exit status:
~~~

## Câu hỏi pass gate

1. Program khác process thế nào?
2. PID và PPID cho biết gì?
3. Process tree được hình thành thế nào?
4. CWD ảnh hưởng application ra sao?
5. Environment được truyền từ parent sang child thế nào?
6. FD giải quyết vấn đề gì?
7. TCP listener liên hệ với process qua cái gì?
8. Vì sao SIGTERM nên được ưu tiên hơn SIGKILL?

## Cleanup

Nếu process vẫn còn chạy:

~~~bash
kill -TERM "$SERVER_PID"
~~~

Nếu không phản hồi:

~~~bash
kill -KILL "$SERVER_PID"
~~~

Xóa log test:

~~~bash
rm -f /tmp/l01-9090.log
~~~

Chỉ xóa đúng file log test đã tạo.

