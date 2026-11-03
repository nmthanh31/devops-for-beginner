# Bài 4 — Baseline, health, readiness và rollback

> **Sau bài này bạn sẽ:**
> - Kiểm một service theo 4 bề mặt: process → listener → HTTP → dependency.
> - Phân biệt health và readiness.
> - Chạy một vòng thay đổi an toàn có baseline, rollback đã verify, và timeline.
>
> **Cần trước:** [Bài 3](./03-recovery-runbook.md), [L02 service lifecycle](../../domain2-Boot&Service/docs/README.md).

## Vì sao backup thôi chưa đủ?

Backup trả lại dữ liệu; vận hành còn cần biết **service có chạy đúng không**, thay đổi nào gây lỗi và làm thế nào trở lại trạng thái tốt. Một `systemctl status active` chỉ chứng minh systemd giữ process theo kỳ vọng của unit. Process đó vẫn có thể không listen, trả `500`, đọc nhầm mount hoặc không kết nối được database.

Hãy xem một service HTTP gồm bốn bề mặt:

```text
unit/process → socket/listener → HTTP endpoint → dependency/data
```

Mỗi mũi tên cần một phép kiểm. `systemctl status` kiểm process; `ss -lntp` kiểm listener; `curl -i` kiểm response; một request đọc dữ liệu hoặc check chuyên dụng kiểm dependency. Nếu chỉ kiểm `/` trả `200` từ trang tĩnh, bạn chưa chứng minh service dùng database được.

## Health và readiness

**Liveness/health** trả lời “process có còn khả năng hoạt động cơ bản không?”. **Readiness** trả lời “nó đã sẵn sàng nhận traffic người dùng chưa?”. Hai kết quả có thể khác nhau: app vẫn chạy và trả `/healthz` nhưng đang chờ migration/database nên chưa ready; load balancer không nên gửi traffic người dùng tới nó. Endpoint `/healthz` hoặc `/readyz` chỉ có nghĩa khi bạn biết chính xác chúng kiểm gì.

Ví dụ một API trả `200` tại `/healthz`, nhưng `/readyz` trả `503` khi không truy cập được database. Đây có thể là hành vi đúng: process sống nhưng tạm không nhận traffic. Nếu load balancer chỉ kiểm TCP connect, nó có thể vẫn gửi request và khách hàng nhận lỗi. Ghi rõ health check của proxy/monitoring đang gọi path nào, kỳ vọng status gì và timeout bao nhiêu.

## Baseline trước khi thay đổi

**Baseline** là trạng thái tốt đã đo được. Trước khi sửa unit hoặc config, lưu:

- bản unit/config và checksum của chúng;
- `systemctl status`, listener `ss`, HTTP response/status/body mong đợi;
- mount, owner/mode, route và resource metric liên quan;
- timestamp UTC và log tại thời điểm đó.

Sau thay đổi, so cùng phép kiểm với baseline. Nếu lỗi xuất hiện, bạn biết biến nào vừa đổi. Tránh vừa đổi service unit, firewall và file permission trong cùng một lần; nhiều biến cùng thay đổi làm chẩn đoán khó hơn.

## Một vòng thay đổi an toàn

1. Viết giả thuyết: “service fail vì WorkingDirectory không tồn tại”, kèm lệnh sẽ xác nhận hoặc bác bỏ.
2. Sao lưu cấu hình lab, ghi lệnh rollback và kiểm đường console/SSH.
3. Chỉ đổi một điều. Với systemd unit, chạy `systemctl daemon-reload` rồi start/restart đúng unit lab.
4. Kiểm từ trong ra ngoài: process → listener → local HTTP → client HTTP → log.
5. Chạy **positive test** cho hành vi phải được phép và **negative test** cho hành vi phải bị từ chối.
6. Nếu không đạt tiêu chí, khôi phục config cũ, reload lại, kiểm service và ghi nguyên nhân thất bại.

Rollback là một thao tác cần **verify**, không phải chỉ copy file cũ rồi kết luận đã an toàn. Nếu schema data đã đổi, rollback binary/config có thể chưa đủ; xem khả năng tương thích data trước khi thực hiện.

## Incident timeline và cold rebuild

Timeline ghi thời điểm phát hiện, triệu chứng phía client, mỗi phép đo, mỗi thay đổi, thời điểm phục hồi và tác động. Ví dụ: `10:02 curl timeout`, `10:04 ss không có listener`, `10:06 journal báo 200/CHDIR`, `10:09 sửa WorkingDirectory`, `10:10 local và remote curl 200`. Timeline giúp người khác kiểm chứng quan hệ nhân quả và tính thời gian khôi phục.

**Cold rebuild** là dựng lại từ môi trường trống bằng artifact, cấu hình, secret được cấp đúng cách và bản backup đã xác minh. Nó kiểm tra runbook có thực sự đủ bước. Nếu service chỉ chạy được vì một file thủ công còn sót trên VM cũ, cold rebuild sẽ phát hiện. Dùng VM lab và data giả cho drill này.

| Bề mặt | Lệnh | Chứng minh |
|---|---|---|
| Unit/process | `systemctl status` | systemd giữ process |
| Socket | `ss -lntp` | Có listener đúng IP:port |
| HTTP | `curl -i http://127.0.0.1:PORT/healthz` | App trả lời |
| Dependency | `curl -i .../readyz` hoặc request đọc data | App dùng được DB/mount |

## Tự kiểm tra

1. `systemctl active`, `ss` có listener, nhưng `/readyz` trả `503`: bạn sẽ kiểm gì tiếp theo?
2. Sau restore, checksum file đúng nhưng API vẫn trả lỗi: checksum đã chứng minh điều gì, còn thiếu phép kiểm nào?
3. Bạn sửa config rồi rollback, nhưng response không trở lại baseline: điều gì có thể đã thay đổi ngoài config?

<details>
<summary>Đáp án</summary>

1. Dependency mà readiness kiểm: DB reachable? mount có đúng (`findmnt`)? Đọc app log tại thời điểm đó.
2. Checksum chứng minh archive không đổi; còn thiếu kiểm owner/mode sau restore, mount đúng, và app đọc được data (application-consistent?).
3. Data/schema đã bị migration đổi, cache, file ngoài config (permission, mount), hoặc quên `daemon-reload`/restart sau khi trả config.

</details>

Nguồn nền: [LPIC-2 Objective 206.2](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V4.5), [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html). Phần health/readiness và cold rebuild là thực hành vận hành mở rộng.
