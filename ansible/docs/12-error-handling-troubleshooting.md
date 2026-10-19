# 12. Error handling và troubleshooting

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Không bắt đầu bằng sửa code. Bắt đầu bằng phân loại lỗi và evidence. Mỗi lỗi cần trả lời: lỗi xảy ra ở lớp nào, lệnh kiểm tra nào xác nhận, thay đổi tối thiểu là gì?

## 1. Cây chẩn đoán

```text
Target đúng chưa?
 ├─ không → inventory/pattern/config
 └─ có
    ↓
Network/DNS/TCP/22?
 ├─ không → route/firewall/hostname
 └─ có
    ↓
SSH user/key/host key?
 ├─ không → authentication/known_hosts/permission
 └─ có
    ↓
Python/become/module/data?
```

`UNREACHABLE` thường là kết nối; `FAILED` là task đã tới host nhưng không đạt. Hai loại này cần hướng xử lý khác nhau.

## 2. Error controls

- `failed_when`: định nghĩa failure có chủ đích;
- `changed_when`: điều chỉnh changed cho command có semantics rõ;
- `ignore_errors`: bỏ qua failed, dùng rất hạn chế;
- `block/rescue/always`: flow recovery/cleanup;
- `until/retries/delay`: chờ eventual consistency;
- `async/poll`: thao tác dài cần job polling.

```yaml
- name: Wait for endpoint
  ansible.builtin.uri:
    url: http://127.0.0.1/health
    status_code: 200
  register: health
  until: health.status == 200
  retries: 10
  delay: 3
```

Retry không sửa được lỗi package name, YAML sai hoặc credential sai; dùng retry đúng cho lỗi tạm thời.

## 3. Error thường gặp

| Error | Lớp cần kiểm tra đầu tiên |
|---|---|
| SSH timeout | IP/DNS/route/firewall/sshd |
| Permission denied | user/key/authorized_keys/permission |
| Python missing | interpreter/package/bootstrap |
| Sudo password | become policy/credential |
| Package missing | distro/package name/repository |
| Template/YAML syntax | file/dòng/indentation |
| Host không tồn tại | inventory, `--list-hosts` |
| Nhầm environment | `-i`, config, group_vars, guard |

## Lệnh cần chạy

**Git Bash/WSL — control node:**

```bash
ansible-inventory -i inventories/lab/hosts.yml --host dev-web
ansible all -i inventories/lab/hosts.yml -m ping -vvv
ansible-playbook -i inventories/lab/hosts.yml playbooks/site.yml --limit dev -vv
ansible-doc ansible.builtin.package
```

**Linux managed node:**

```bash
python3 --version
systemctl status ssh --no-pager
sudo -n true
getent hosts <target-name>
```

## Thực hành cuối chương: report lỗi

Cố ý tạo một lỗi inventory, một lỗi sudo hoặc một lỗi template. Với mỗi lỗi, ghi:

```text
Lệnh:
Target/inventory:
Error block:
Lớp lỗi:
Lệnh kiểm tra:
Sửa tối thiểu:
```

Không gửi log `-vvv` nguyên vẹn nếu có secret.

## Tài liệu chính thức

- [Error handling in playbooks](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html)
- [Blocks](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_blocks.html)
- [Asynchronous actions](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_async.html)

