# L01 — Linux Execution Model

> Tài liệu lý thuyết được tách theo từng bài để dễ học và tra cứu. Phần lab nằm riêng trong thư mục ../lab/.

## Mục tiêu

Sau buổi này, có thể nhìn vào một process bất kỳ và trả lời:

- Nó đang chạy program nào?
- Ai tạo ra nó?
- PID và PPID là gì?
- Nó chạy dưới user/group nào?
- Nó đang đứng ở thư mục nào?
- Nó có environment gì?
- Nó đang mở file, pipe hoặc socket nào?
- Nó đang ở state nào?
- Nếu gửi signal thì chuyện gì xảy ra?
- Khi kết thúc, nó trả exit code nào?

## Lộ trình lý thuyết

0. [Command Reference — toàn bộ Buổi 1](./00-command-reference.md)
1. [Program và Process](./01-program-process.md)
2. [Process được tạo như thế nào](./02-process-creation.md)
3. [PID, PPID và Process Tree](./03-pid-ppid-process-tree.md)
4. [/proc — Cửa sổ nhìn vào process](./04-proc.md)
5. [Executable và CWD](./05-executable-cwd.md)
6. [Environment Variables](./06-environment.md)
   - [Danh sách câu lệnh Environment](./06-environment-commands.md)
7. [UID/GID và Process Credentials](./07-uid-gid.md)
8. [File Descriptor](./08-file-descriptor.md)
9. [Process và TCP Socket](./09-tcp-socket.md)
10. [Thread và Process State](./10-thread-process-state.md)
11. [Signal](./11-signal.md)
12. [Exit Code](./12-exit-code.md)
13. [Tổng hợp Execution Model](./13-summary-execution-model.md)

## Mental model tổng quát

~~~text
program
   ↓ exec()
process
   ├── PID / PPID
   ├── UID / GID
   ├── environment
   ├── CWD
   ├── memory
   ├── threads
   ├── file descriptors
   ├── signal handling
   └── exit status
~~~

## Pass Gate

Không nhìn tài liệu, hãy tự giải thích được:

1. Program khác Process thế nào?
2. PID và PPID cho biết điều gì?
3. Process tree được hình thành thế nào?
4. CWD ảnh hưởng application ra sao?
5. Environment được truyền từ parent sang child thế nào?
6. FD thực chất giải quyết vấn đề gì?
7. TCP listener liên hệ với process qua cái gì?
8. Tại sao SIGTERM nên được ưu tiên hơn SIGKILL?

Sau khi hoàn thành phần lý thuyết, mới chuyển sang lab.

