# L07 — Linux Logs, Time & Timers

Domain này học ba năng lực vận hành liên quan chặt với nhau: đọc log để biết chuyện gì xảy ra, giữ system time chính xác, và lên lịch job tự động.

## Theory

Đọc theo thứ tự trong [docs](./docs/README.md).

Thực hành trong [L07 Labs](./lab/README.md).

Nội dung core đối chiếu LPIC-1 Objective **107.2 — Scheduling jobs**, **108.1 — Maintain system time** và **108.2 — System logging**. [Nguồn chính thức LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

## Chuỗi cần nhớ

```text
event/process → log → query/filter → diagnosis
clock/timezone → timestamp đúng → log và scheduler đáng tin
schedule → job → output/log → verify
```

