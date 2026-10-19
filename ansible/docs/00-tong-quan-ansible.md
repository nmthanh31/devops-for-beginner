# 00. Ansible và kiến trúc automation

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Sau chương này, bạn chưa cần viết role. Bạn chỉ cần làm được ba việc:

1. Chỉ ra control node, managed node, inventory, module và SSH trong một flow.
2. Nhìn một task và giải thích Ansible sẽ kiểm tra/truyền/thực thi gì.
3. Chọn đúng ranh giới giữa Terraform, Ansible và các công cụ xung quanh.

## 1. Ansible là gì?

Ansible là công cụ automation dùng để đưa một nhóm máy hoặc dịch vụ về trạng thái mong muốn. Nó thường được dùng cho:

- cài đặt package;
- quản lý user, group, file và permission;
- cấu hình service và systemd;
- render configuration bằng template;
- triển khai ứng dụng;
- kiểm tra trạng thái và thực hiện thao tác vận hành có kiểm soát.

Ansible không chỉ là một tập lệnh SSH. Điểm quan trọng là task mô tả **trạng thái**:

```yaml
- name: Nginx phải được cài
  ansible.builtin.package:
    name: nginx
    state: present
```

Task không nói “hãy chạy lệnh cài nginx mỗi lần”. Nó nói “sau task này, package nginx phải tồn tại”. Module chịu trách nhiệm đọc trạng thái hiện tại và quyết định có cần thay đổi hay không.

## 2. Mô hình cần ghi nhớ

```text
                         Control node
                  ┌────────────────────────┐
                  │ inventory + playbook  │
                  │ Ansible Core          │
                  └───────────┬────────────┘
                              │ SSH
                 ┌────────────┴────────────┐
                 ▼                         ▼
          ansible-dev                ansible-stag
          managed node               managed node
```

| Thành phần | Trả lời câu hỏi |
|---|---|
| Control node | Ansible chạy ở đâu? |
| Managed node | Máy nào nhận và thực thi module? |
| Inventory | Ansible chọn host nào và kết nối thế nào? |
| Module | Công việc cụ thể được thực hiện bằng abstraction nào? |
| Task | Một lần gọi module có tên rõ ràng |
| Play | Ánh xạ tasks/roles vào một nhóm host |
| Playbook | File YAML chứa một hoặc nhiều play |
| Role | Đơn vị đóng gói có cấu trúc để tái sử dụng |
| Handler | Task phản ứng với một thay đổi đã xảy ra |

## 3. Execution flow của một task

Khi chạy một playbook, có thể hình dung flow như sau:

```text
Playbook
   ↓ đọc hosts/pattern
Inventory ──→ chọn host + biến kết nối
   ↓
SSH từ control node
   ↓
Ansible truyền module/arguments
   ↓
Managed node kiểm tra trạng thái
   ↓
Không đổi → ok     Cần đổi → changed
   ↓
Handler được notify nếu có thay đổi
```

Mô hình này giải thích vì sao Ansible cần SSH, vì sao inventory sai làm task chạy nhầm, và vì sao module thường tốt hơn việc ghép shell command.

## 4. Agentless và SSH

Agentless nghĩa là managed node không cần chạy một Ansible agent liên tục để chờ lệnh. Control node mở kết nối khi cần, gửi module, nhận kết quả rồi kết thúc phiên thực thi.

SSH cung cấp:

- xác thực user bằng password hoặc key;
- mã hóa đường truyền;
- kiểm tra host key;
- kênh để Ansible thực thi module.

Agentless không có nghĩa là managed node không cần điều kiện gì. Thông thường cần SSH server, user phù hợp và Python. `raw` có thể hỗ trợ bootstrap trong trường hợp Python chưa có, nhưng không phải lựa chọn bình thường.

## 5. Ansible khác Terraform ở đâu?

Terraform thường quản lý lifecycle của infrastructure thông qua provider/API và state. Ansible thường quản lý configuration và application state bên trong host hoặc qua API.

```text
Developer → Git → Terraform → VM/Kubernetes → Ansible → Application
```

| Câu hỏi | Terraform | Ansible |
|---|---|---|
| Tạo VM/network/cluster? | Phù hợp | Không phải trọng tâm |
| Cài package trong VM? | Không phù hợp | Phù hợp |
| Có state file riêng? | Có state làm source mapping | Không có state trung tâm cùng kiểu Terraform |
| Kết nối chính | Provider/API | SSH hoặc API/module |
| Mô hình | Infrastructure provisioning | Configuration/deployment automation |
| Chạy lại | Plan so sánh config/state/thực tế | Module kiểm tra trạng thái và thay đổi cần thiết |

Ranh giới không tuyệt đối, nhưng ownership phải rõ. Ví dụ Terraform tạo VM và IP; Ansible cài Nginx, render `/etc/nginx`, tạo systemd service.

## 6. Ansible khác các công cụ xung quanh

- Docker đóng gói và chạy container image; Ansible có thể cài Docker hoặc deploy container.
- Kubernetes điều phối workload trong cluster; Ansible có thể cấu hình cluster hoặc gọi Kubernetes API.
- GitLab Runner là nơi chạy CI job; nó có thể là control node tạm thời.
- Atlantis điều phối workflow Terraform qua Merge Request; nó không thay thế Ansible.

## Thực hành cuối chương: đọc kiến trúc một project

Mở `ansible-jun/ansible.cfg`, inventory và một role hiện có. Ghi lại:

| Câu hỏi | Câu trả lời cần có |
|---|---|
| Ansible chạy ở đâu? | Control node nào? |
| Host được chọn ở đâu? | Inventory/pattern nào? |
| Kết nối bằng user/key nào? | Biến inventory nào? |
| Thay đổi được thực hiện bằng gì? | Module/task/role nào? |
| Service reload ở đâu? | Handler nào? |

Hoàn thành chương khi bạn tự mô tả được:

```text
playbook → inventory → SSH → module → managed node → recap
```

## Quy tắc an toàn

- Không gửi private key, password, kubeconfig hoặc Vault password lên Git/chat.
- Luôn xem inventory và target trước task có thay đổi.
- Không dùng shell để thay thế module chuyên dụng.
- Không để Terraform và Ansible cùng sở hữu một file/lifecycle.

## Tài liệu chính thức

- [Ansible introduction](https://docs.ansible.com/ansible/latest/get_started/get_started.html)
- [Ansible concepts](https://docs.ansible.com/ansible/latest/getting_started/basic_concepts.html)
- [Connections and delegation](https://docs.ansible.com/ansible/latest/inventory/connection_details.html)

