# Bài 6 — Baseline, lấy mẫu và capacity trend

<!-- learn:head -->
> **Sau bài này bạn sẽ:** lấy baseline có interval (không chỉ snapshot), dùng `sar` cho dữ liệu lịch sử, và đọc xu hướng capacity.
>
> **Hình dung:** không biết huyết áp bình thường của bạn là bao nhiêu thì con số hôm nay không có nghĩa — baseline là "lúc khỏe trông thế nào".


## Baseline là gì?

Baseline là trạng thái tài nguyên bình thường của hệ thống dưới một workload đã biết. Không có baseline, bạn chỉ biết một con số “cao” hoặc “thấp”, nhưng chưa biết nó có bất thường với máy này hay không.

Baseline nên ghi tối thiểu:

- thời gian, timezone và hostname;
- số CPU và dung lượng RAM;
- load, CPU breakdown, runnable/blocked task;
- memory available và swap activity;
- throughput, latency và queue của disk;
- workload hoặc số request tại thời điểm đo.

## Snapshot và interval

Một lệnh chạy một lần chỉ là snapshot. Sự cố hiệu năng cần quan sát theo khoảng thời gian:

```bash
vmstat 1 10
iostat -xz 1 10
pidstat 1 10
```

Ý nghĩa:

- lấy mẫu mỗi một giây;
- tổng cộng mười lần;
- quan sát xem áp lực kéo dài hay chỉ là spike ngắn.

Với nhiều công cụ, dòng đầu có thể phản ánh trung bình từ lúc boot. Cần đọc tài liệu của công cụ và tập trung vào các mẫu tiếp theo khi điều tra hiện tại.

## Dữ liệu lịch sử với `sar`

`sar` thuộc bộ `sysstat`. Nếu hệ thống đã bật thu thập lịch sử, nó giúp xem trạng thái tại lúc sự cố đã qua:

```bash
sar -u
sar -r
sar -q
sar -d
```

- `-u`: CPU.
- `-r`: memory.
- `-q`: run queue và load.
- `-d`: block device.

Nếu chưa bật thu thập từ trước, `sar` không thể tạo lại quá khứ. Monitoring phải được chuẩn bị trước incident.

## Capacity trend

Capacity planning không dựa vào một peak duy nhất. Cần theo dõi:

```text
giá trị theo thời gian
    + tốc độ tăng trưởng
    + workload tương ứng
    + headroom còn lại
    = dự đoán thời điểm chạm giới hạn
```

Ví dụ, memory tăng đều mỗi ngày đáng quan tâm hơn một spike đã trở lại baseline. Disk latency tăng theo lượng request có thể cho thấy giới hạn throughput đang đến gần.

## Evidence phải tái lập được

Khi lưu bằng chứng, ghi cả command và thời gian:

```bash
date --iso-8601=seconds
hostname
uptime
free -h
vmstat 1 5
iostat -xz 1 5
```

Không công khai command line hoặc environment có chứa password, token hay dữ liệu nội bộ.

## Nguồn

- [LPIC-2 V4.5 — Objectives 200.1 và 200.2](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5)
