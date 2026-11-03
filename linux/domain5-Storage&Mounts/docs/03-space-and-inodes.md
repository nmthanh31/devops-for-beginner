# Bài 3 — Dung lượng bytes, inode và filesystem đầy

<!-- learn:head -->
> **Sau bài này bạn sẽ:**
> - Phân biệt "đầy bytes" và "đầy inode" — cùng lỗi `No space left on device`.
> - Giải thích vì sao `df` và `du` có thể lệch.
>
> **Hình dung:** bãi đỗ xe có giới hạn **diện tích** (bytes) và giới hạn **số vé** (inode). Hết vé thì xe nhỏ cũng không vào được dù còn chỗ.


> **LPIC-1:** Objective 104.2 yêu cầu theo dõi dung lượng trống và inode, đồng thời biết kiểm tra tính toàn vẹn filesystem và sửa một số lỗi cơ bản.

## Hai tài nguyên filesystem phải theo dõi

### Bytes/blocks

Filesystem dành các block để lưu nội dung file. Khi các block trống cạn, không ghi thêm được dữ liệu đáng kể. `df -h` cho biết dung lượng tổng, đã dùng và còn trống theo đơn vị dễ đọc.

### Inodes

Filesystem cũng cần inode để lưu metadata của từng file và thư mục. Mỗi file rỗng vẫn cần inode. Nếu hết inode, việc tạo file mới có thể thất bại dù `df -h` vẫn báo còn nhiều dung lượng.

`df -i` hiển thị lượng inode đã dùng và còn trống.

| Quan sát | Câu hỏi cần trả lời |
|---|---|
| `df -h` | Còn block/bytes để ghi nội dung không? |
| `df -i` | Còn inode để tạo thêm file/thư mục không? |

## `df` khác `du`

- `df` xem dung lượng mà filesystem báo đã dùng/còn trống.
- `du` cộng dung lượng của file/thư mục được chỉ định.

Hai kết quả có thể khác nhau, ví dụ do file đã bị xóa khỏi tên thư mục nhưng còn được process mở, hoặc do metadata/reserved space của filesystem. Vì vậy dùng `du` để tìm thư mục lớn không thay thế được `df` để đánh giá filesystem.

## Kiểm tra integrity không đồng nghĩa với kiểm tra dung lượng

`df`/`du` giúp tìm vấn đề dung lượng; công cụ kiểm tra filesystem như `fsck` hoặc công cụ riêng theo filesystem giải quyết một lớp vấn đề khác. Không chạy lệnh sửa filesystem trên thiết bị đang được mount theo cách không an toàn. Trước khi sửa, xác định đúng filesystem, trạng thái mount và kế hoạch backup/restore.

<!-- learn:tail -->
## Bảng chẩn đoán

| `df -h` | `df -i` | Nguyên nhân hay gặp | Tìm bằng |
|---|---|---|---|
| 100% | thấp | File lớn | `du -xh --max-depth=1 / \| sort -h` |
| thấp | 100% | Hàng triệu file nhỏ (cache, session) | `find /path -xdev -type f \| wc -l` theo thư mục |
| cao, `du` thấp hơn nhiều | — | Open-unlinked file | `lsof +L1` ([L03](../../domain3-Filesystem&Path/docs/04-open-unlinked-files.md)) |
| cao, `du` thấp hơn | — | Dữ liệu bị che dưới mount point | `umount` tạm / bind mount `/` sang chỗ khác để xem |

## Tự kiểm tra

1. `touch x` báo `No space left on device`, `df -h` còn 40%. Kiểm gì?
2. `df` báo dùng 30G, `du -sh /` chỉ 18G. Hai giả thuyết?

<details>
<summary>Đáp án</summary>

1. `df -i` — có thể hết inode.
2. Open-unlinked file đang được process giữ; hoặc dữ liệu nằm dưới một mount point (bị che).

</details>

## Nguồn

- [LPIC-1 104.2 — Maintain the integrity of filesystems](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- Tham khảo lệnh: `man df`, `man du`, `man fsck`, và trang man tương ứng với filesystem.

