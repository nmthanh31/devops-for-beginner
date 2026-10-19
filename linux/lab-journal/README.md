# Linux Lab Journal

Thư mục này dùng để ghi lại các buổi lab Linux đã làm: đề bài, dự đoán, lệnh/kết quả, lỗi đã gặp, cách xử lý và điều đã học được.

## Cách ghi một buổi lab

1. Tạo một file Markdown theo mẫu `YYYY-MM-DD-ten-buoi-lab.md`.
2. Trước khi chạy lệnh, ghi dự đoán và giả thuyết.
3. Lưu command/output cần thiết; xóa hoặc che thông tin nhạy cảm.
4. Ghi rõ nguyên nhân, thay đổi tối thiểu, cách verify và cleanup.
5. Cuối buổi tự giải thích lại cơ chế bằng lời của mình.

Các bài lab gốc theo domain vẫn nằm trong thư mục `domain*/lab`. Journal này là nơi lưu quá trình thực hành và kết quả cá nhân.

## Lab đã ghi

- [2026-10-17 — Tự dựng độc lập Linux core (L01–L04)](./L01-L04/2026-10-17-w3-independent-linux-core.md)
- [Lab 2 — Shared read-only content cho service](./L01-L04/2026-10-17-lab2-shared-readonly-service.md)
- [2026-10-18 — W3 Linux Core: Deepen/Repair + Gate](./L01-L04/2026-10-18-w3-linux-core-deepen-gate.md)
- [W3 — Linux Core Main Labs (L01–L04)](./L01-L04/W3-linux-core-main-labs.md)

## Mẫu ghi nhanh

~~~markdown
# YYYY-MM-DD — Tên bài lab

## Mục tiêu

## Môi trường và phạm vi an toàn
- Host/VM:
- Có thể dùng sudo không:
- Phạm vi được phép thay đổi:

## Dự đoán trước khi chạy

## Các bước và bằng chứng
| Bước | Lệnh/thao tác | Dự đoán | Kết quả thực tế | Giải thích |
|---|---|---|---|---|

## Lỗi / troubleshooting
| Triệu chứng | Bằng chứng | Nguyên nhân | Sửa tối thiểu | Verify |
|---|---|---|---|---|

## Definition of Done
- [ ]

## Cleanup

## Explain-back

## Câu hỏi còn lại
~~~
