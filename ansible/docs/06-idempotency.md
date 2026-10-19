# 06. Idempotency và trạng thái thay đổi

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Đừng chỉ nhìn playbook “chạy không lỗi”. Hãy chạy hai lần, so sánh recap, giải thích từng `changed`, rồi dùng check/diff để chứng minh trạng thái.

## 1. Idempotency là gì?

Một automation idempotent có thể chạy lại nhiều lần mà sau lần đầu không tạo thêm thay đổi không cần thiết:

```text
Desired state ── apply ──→ state đúng
state đúng    ── apply ──→ không đổi
```

Idempotency giúp retry an toàn hơn, review dễ hơn, giảm service restart và giảm drift do thao tác thủ công.

## 2. Đọc recap

| Trạng thái | Ý nghĩa |
|---|---|
| `ok` | Task chạy, trạng thái đã đúng |
| `changed` | Task đã thay đổi host |
| `failed` | Task chạy nhưng thất bại |
| `skipped` | Điều kiện/tag không cho task chạy |
| `unreachable` | Control node không kết nối được host |

`changed` không đồng nghĩa lỗi. Nhưng mỗi changed ở lần chạy thứ hai phải có lý do: timestamp, service backend, command hoặc module không hỗ trợ check.

## 3. Vì sao module tốt hơn shell?

```yaml
- name: Desired directory state
  ansible.builtin.file:
    path: /opt/example
    state: directory
```

So với `mkdir -p /opt/example`, module biết state và thường tự báo `ok` khi đã đúng. Shell chỉ biết exit code; nó không tự biết nội dung/permission đã đúng hay chưa.

Nếu bắt buộc command/shell, dùng guard `creates`/`removes`, `changed_when`, `failed_when` và mô tả rõ vì sao không có module phù hợp. Không dùng `changed_when: false` để che lỗi.

## 4. Check mode và diff mode

`--check` cố gắng dự đoán thay đổi; `--diff` hiển thị nội dung file trước/sau ở module hỗ trợ. Chúng không mô phỏng hoàn hảo mọi command và diff có thể làm lộ secret.

## Thực hành cuối chương: chứng minh lần chạy thứ hai

```bash
ansible-playbook -i inventories/lab/hosts.yml playbooks/web.yml
ansible-playbook -i inventories/lab/hosts.yml playbooks/web.yml
ansible-playbook -i inventories/lab/hosts.yml playbooks/web.yml --check --diff
```

Ghi lại hai recap trong bảng:

| Lần chạy | changed | ok | failed | Giải thích |
|---|---:|---:|---:|---|
| 1 | ? | ? | ? | resource được tạo/cập nhật |
| 2 | ? | ? | ? | vì sao còn/không còn changed |

Hoàn thành khi lần hai không có thay đổi không cần thiết.

## Tài liệu chính thức

- [Check mode](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Handlers](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html)
- [Error handling](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html)

