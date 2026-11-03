# Bài 5 — Liên hệ bằng chứng và tìm bottleneck

<!-- learn:head -->
> **Sau bài này bạn sẽ:** ghép host metric + process metric + log **cùng timestamp** để xác định bottleneck, rồi sửa tối thiểu và verify bằng so sánh before/after.


## Bottleneck là gì?

Bottleneck là thành phần đang giới hạn throughput hoặc làm latency tăng trong đường đi của công việc.

```text
client → network → service → CPU/memory → filesystem → block device
```

Thành phần có mức sử dụng cao chưa chắc là bottleneck. Bottleneck phải giải thích được triệu chứng và timeline.

## Các mẫu evidence thường gặp

### CPU saturation

```text
ứng dụng chậm
+ CPU idle thấp kéo dài
+ vmstat r cao
+ process hoặc thread phù hợp đứng đầu CPU
= nghi CPU saturation
```

### I/O bottleneck

```text
ứng dụng chậm
+ load cao nhưng CPU vẫn còn idle
+ vmstat b/wa tăng
+ iostat await/aqu-sz tăng
+ process liên quan đang đọc/ghi
= nghi I/O bottleneck
```

### Memory pressure

```text
ứng dụng chậm hoặc bị kill
+ available thấp theo thời gian
+ swap in/out hoạt động liên tục
+ process RSS tăng hoặc có OOM log
= nghi memory pressure
```

### Chưa thấy host bottleneck

Nếu CPU còn rảnh, memory không pressure, I/O không có hàng đợi nhưng API vẫn chậm, hãy mở rộng giả thuyết:

- application lock hoặc thread pool;
- dependency/database chậm;
- DNS hoặc network;
- timeout/retry;
- giới hạn bên trong container/cgroup dù host còn dư tài nguyên.

Không tìm thấy host bottleneck cũng là một kết quả có giá trị: nó giúp loại một nhánh điều tra.

## Observation surface

| Câu hỏi | Bề mặt quan sát phù hợp |
|---|---|
| Host có pressure chung không? | `uptime`, `vmstat`, `free` |
| Process nào dùng CPU/memory? | `top`, `ps`, `pidstat` |
| Disk nào đang chờ lâu? | `iostat -xz` |
| Process nào tạo I/O? | `iotop`, `pidstat -d`, `lsof` |
| Có OOM hoặc lỗi kernel không? | `journalctl -k`, `dmesg` |
| Service có bị giới hạn bởi systemd/cgroup không? | `systemctl show`, `systemd-cgtop` |

## Sửa tối thiểu và verify

Sau khi có giả thuyết:

1. Chọn thay đổi nhỏ nhất có thể kiểm chứng nguyên nhân.
2. Lưu trạng thái/config trước khi đổi.
3. Thực hiện positive test: chức năng cần thiết hoạt động.
4. Thực hiện negative test: trường hợp không được phép hoặc fault cũ không còn tái hiện.
5. So metric trước và sau trong cùng loại workload.

Không nên “tối ưu” nhiều thông số cùng lúc vì sẽ không biết thay đổi nào thực sự có tác dụng.

<!-- learn:tail -->
## Bảng tra nhanh

| Mẫu | `vmstat` | Khác |
|---|---|---|
| CPU saturation | `r` > số CPU, `us+sy` cao | `pidstat -u` chỉ ra process |
| I/O bottleneck | `b` > 0, `wa` cao | `iostat -x` await cao, process `D` |
| Memory pressure | `si/so` > 0, `free` thấp | `available` thấp, journal OOM |
| Không thấy host bottleneck | mọi thứ bình thường | Nghi app/dependency/network (L10) |

## Nguồn

- [LPIC-2 V4.5 — Objective 200.1](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
