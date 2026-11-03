# Tài liệu lý thuyết Python

Bộ tài liệu gồm hai phần: nền tảng ngôn ngữ Python và lý thuyết ứng dụng Python để xây dựng web API, webhook và công cụ tự động hóa. Tài liệu giải thích khái niệm, vai trò, lý do dùng và giới hạn; không yêu cầu bạn sao chép một ứng dụng hoàn chỉnh.

## Lộ trình học

1. [Lộ trình và cách học](00-lo-trinh.md)
2. [Cú pháp và kiểu dữ liệu cơ bản](01-cu-phap-va-kieu-du-lieu.md)
3. [Cấu trúc dữ liệu](02-cau-truc-du-lieu.md)
4. [Điều kiện, vòng lặp và hàm](03-dieu-khien-va-ham.md)
5. [Module, package và môi trường ảo](04-module-package-moi-truong-ao.md)
6. [Ngoại lệ, file và dữ liệu JSON](05-ngoai-le-file-json.md)
7. [Lập trình hướng đối tượng](06-lap-trinh-huong-doi-tuong.md)
8. [Type hints, kiểm thử và quy tắc viết code](07-type-hints-kiem-thu.md)
9. [Kiến thức Python thực tế](08-python-thuc-te.md)

## Lý thuyết web, API và công cụ

10. [Tư duy thiết kế ứng dụng web và công cụ](09-tu-duy-thiet-ke-ung-dung.md)
11. [Nền tảng web, HTTP và API](10-web-http-api.md)
12. [FastAPI và Pydantic](11-fastapi-pydantic.md)
13. [Kiến trúc ứng dụng web và phân chia trách nhiệm](12-kien-truc-ung-dung.md)
14. [Gọi dịch vụ HTTP, httpx và async](13-http-client-async.md)
15. [JSON, PostgreSQL, Redis và tính nhất quán dữ liệu](14-json-postgres-redis.md)
16. [Kiểm thử ứng dụng Python](15-kiem-thu-python.md)
17. [Cấu hình, bảo mật và quản lý lỗi](16-cau-hinh-bao-mat.md)
18. [Viết công cụ dòng lệnh bằng Python](17-python-cli-tools.md)
19. [Docker, health check, log và metrics](18-van-hanh-docker-observability.md)

Tài liệu hướng dẫn một ứng dụng cụ thể không đặt trong bộ lý thuyết này; mỗi dự án có README riêng trong thư mục của dự án.

## Yêu cầu tối thiểu

- Python 3.11 trở lên.
- Một trình soạn thảo mã nguồn.
- Có thể chạy lệnh `python --version` trong terminal.

## Nguyên tắc học

- Đọc khái niệm, sau đó tự gõ lại ví dụ thay vì chỉ sao chép.
- Dùng tên biến rõ nghĩa và định dạng code nhất quán.
- Khi gặp lỗi, đọc traceback từ dòng cuối lên để tìm nguyên nhân gần nhất.
- Mỗi chủ đề nên được củng cố bằng một chương trình nhỏ.
- Với mỗi thành phần mới, hãy tự trả lời ba câu: nó giải quyết vấn đề gì, nhận dữ liệu gì, và có trách nhiệm gì trong luồng ứng dụng?
- Khi học một thư viện, trước tiên hiểu khái niệm mà thư viện đang tự động hóa; sau đó mới học API/cú pháp cụ thể.
