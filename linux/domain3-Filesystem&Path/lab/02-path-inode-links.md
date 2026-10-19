# Lab 2 — Path lookup, inode và links

## Mục tiêu

Tạo hard link và symlink trong thư mục riêng, rồi dùng `stat`, `ls -li`, `namei` và `readlink` để chứng minh hai loại link khác nhau.

## Bước 1 — Tạo scratch area

~~~bash
LAB_DIR=$(mktemp -d "$HOME/l03-links.XXXXXX")
printf 'L03 inode and link lab\n' > "$LAB_DIR/original.txt"
~~~

Ghi lại `LAB_DIR` để dùng tới cuối bài.

## Bước 2 — Tạo hai loại link

~~~bash
ln "$LAB_DIR/original.txt" "$LAB_DIR/hard.txt"
ln -s original.txt "$LAB_DIR/symbolic.txt"
~~~

Symlink cố ý dùng target tương đối; target được hiểu tương đối từ thư mục chứa `symbolic.txt`.

## Bước 3 — Thu evidence

~~~bash
ls -li "$LAB_DIR"
stat -c 'device=%d inode=%i links=%h type=%F name=%n' "$LAB_DIR/original.txt" "$LAB_DIR/hard.txt" "$LAB_DIR/symbolic.txt"
readlink "$LAB_DIR/symbolic.txt"
namei -l "$LAB_DIR/symbolic.txt"
~~~

Trả lời trước khi tiếp tục:

1. Hai path nào có cùng `device` và `inode`?
2. Vì sao symlink có inode riêng?
3. `readlink` cho biết path nào?
4. Link count của hard-linked object thay đổi ra sao?

## Bước 4 — Đổi nội dung qua một tên

~~~bash
printf 'Changed through hard link\n' > "$LAB_DIR/hard.txt"
cat "$LAB_DIR/original.txt"
cat "$LAB_DIR/symbolic.txt"
~~~

Giải thích vì sao nội dung qua cả ba tên phản ánh cùng một thay đổi.

## Bước 5 — Xóa tên gốc và quan sát

~~~bash
rm "$LAB_DIR/original.txt"
ls -li "$LAB_DIR"
cat "$LAB_DIR/hard.txt"
cat "$LAB_DIR/symbolic.txt"
~~~

Hard link vẫn đọc được; symlink tương đối giờ dangling vì `original.txt` đã mất. Dùng `namei -l "$LAB_DIR/symbolic.txt"` để thấy thành phần đường dẫn bị thiếu.

## Dọn lab

~~~bash
rm -f "$LAB_DIR/hard.txt" "$LAB_DIR/symbolic.txt"
rmdir "$LAB_DIR"
~~~

Lệnh chỉ dọn các file lab trong thư mục `$LAB_DIR` đã tạo.

