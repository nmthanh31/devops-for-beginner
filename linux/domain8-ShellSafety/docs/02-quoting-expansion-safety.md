# Bài 2 — Quoting, expansion và pathname an toàn

## Vì sao quoting quan trọng?

Shell không truyền nguyên dòng bạn gõ cho program. Nó thực hiện expansion và tách từ trước. Nếu path có dấu cách hoặc ký tự đặc biệt mà không quote, một path có thể bị tách thành nhiều argument.

```bash
file="/srv/my data/report.txt"
cat "$file"
```

`"$file"` bảo vệ toàn bộ giá trị như một argument. Đây là thói quen quan trọng nhất khi dùng biến chứa path.

## Ba loại quote cơ bản

- **Single quote `'...'`:** giữ gần như nguyên văn; variable không được expand.
- **Double quote `"..."`:** vẫn expand variable và command substitution, nhưng giữ khoảng trắng trong một word.
- **Không quote:** shell có thể word-split và pathname-expand bằng globbing.

## Command substitution

`$(command)` lấy stdout của command và chèn vào command hiện tại. Cần quote kết quả nếu kết quả có thể chứa khoảng trắng hoặc ký tự glob.

## Globbing

Các ký tự như `*`, `?`, `[...]` được shell mở rộng thành danh sách pathname trước khi program chạy. Đây không phải regex.

Vì vậy command như `rm "$dir"/*` cần được suy nghĩ kỹ: nếu biến rỗng, path ngoài ý muốn có thể xuất hiện; nếu thư mục chứa nhiều file, command nhận rất nhiều argument.

## Không dùng `eval` tùy tiện

`eval` yêu cầu shell parse lại chuỗi đã tạo. Nếu chuỗi chứa input chưa tin cậy, nó có thể biến dữ liệu thành command. Phần lớn script không cần `eval`.

## Nguồn

- [LPIC-1 103.1/103.3 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)

