# L08 — Shell Safety & Bash Automation

Domain này học cách dùng Bash an toàn và viết script nhỏ có thể dự đoán được: xử lý biến, quoting, exit code, input, pipeline, file và cleanup.

## Theory

Đọc theo thứ tự trong [docs](./docs/README.md).

Thực hành trong [L08 Labs](./lab/README.md).

Nội dung core đối chiếu LPIC-1 Objective **103.1 — Work on the command line**, **103.3 — Basic file management**, **103.4 — Streams, pipes and redirects**, **105.1 — Shell environment** và **105.2 — Simple shell scripts**. [Nguồn chính thức LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

## Chuỗi cần nhớ

```text
input → parse/quote → command → exit status → decision → output/cleanup
```

Script an toàn không chỉ là script chạy được; nó phải xử lý đúng khoảng trắng, input rỗng, lỗi command, path nguy hiểm và trạng thái dở dang.

