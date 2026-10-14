# Bài 3 — Dependency và thứ tự khởi động

> **Phần mở rộng:** LPIC-1 101.3 yêu cầu quản lý runlevel/boot target. `Wants=`, `Requires=`, `After=` và `Before=` ở bài này là đào sâu systemd để hiểu thứ tự và phụ thuộc giữa service, không phải danh sách cốt lõi cần thuộc cho mục tiêu LPIC.
>
> Nguồn phạm vi: [LPI LPIC-1 Objectives V5.0](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0), mục 101.3. Tham khảo directive mở rộng: [systemd.unit(5)](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html).

## Mục tiêu

Phân biệt “kéo unit khác vào để start” với “sắp xếp thứ tự start”.

## Hai câu hỏi riêng

Giả sử api.service cần PostgreSQL:

1. Khi start API, có yêu cầu start PostgreSQL không?
2. Nếu cả hai có start job, unit nào phải bắt đầu trước?

Hai câu hỏi này dùng các directive khác nhau.

## Ordering: After và Before

~~~ini
[Unit]
After=postgresql.service
~~~

After chỉ sắp xếp thứ tự nếu cả hai unit có job phù hợp. Nó không tự yêu cầu PostgreSQL khởi động.

Before diễn đạt ordering ngược lại.

Ordering không chứng minh dependency đã sẵn sàng nhận request; nó chỉ sắp xếp mốc startup theo systemd.

## Requirement: Wants và Requires

~~~ini
Wants=postgresql.service
~~~

Khi unit chính được kích hoạt, systemd cũng cố gắng kéo PostgreSQL vào. Đây là quan hệ yếu hơn; lỗi dependency không nhất thiết làm unit chính không start.

~~~ini
Requires=postgresql.service
After=postgresql.service
~~~

Requires là requirement mạnh hơn. Nếu dependency bắt buộc không start thành công, start job của unit chính có thể thất bại. Nó cũng có tác động trong một số thao tác stop/restart tường minh.

Requires không giám sát liên tục để bảo đảm dependency khỏe trong suốt vòng đời application.

## Bảng ghi nhớ

| Directive | Ý nghĩa |
|---|---|
| After=B | A được sắp xếp sau B khi cả hai có start job |
| Before=B | A được sắp xếp trước B |
| Wants=B | Khi kéo A, cố gắng kéo B vào |
| Requires=B | A cần B theo requirement mạnh hơn |

Application vẫn cần retry, timeout và xử lý mất kết nối.

## Network target không phải health check

After=network-online.target không chứng minh DNS, remote host, database hoặc upstream API đang phản hồi. Ý nghĩa thực tế còn phụ thuộc network manager và wait-online service.

## Lab 1 — Đọc dependency graph (read-only)

~~~bash
systemctl list-unit-files --type=service
systemctl list-dependencies ssh.service
~~~

Nếu ssh.service không tồn tại, thay bằng unit có sẵn. Ghi lại:

- unit nào được liệt kê;
- output cho biết loại quan hệ nào;
- vì sao nó không chứng minh dependency healthy.

## Lab 2 — Tình huống After

Với cấu hình:

~~~ini
[Unit]
After=redis.service
~~~

Tự trả lời:

1. Start api.service có tự yêu cầu start Redis không?
2. Nếu cả hai có start job, thứ tự ra sao?
3. After có chứng minh Redis nhận được kết nối không?

Đáp án: Không; API được sắp xếp sau Redis nếu cả hai có job; điều này không chứng minh Redis sẵn sàng nhận kết nối.

## Cần nhớ

Requirement quyết định unit nào được kéo vào; ordering quyết định thứ tự giữa các job. Chúng không thay thế retry hoặc health check của application.
