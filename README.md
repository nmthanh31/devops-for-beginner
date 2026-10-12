# DevOps / Platform Learning Workspace

Đây là thư mục gốc lưu toàn bộ nội dung học, lab, tài liệu và evidence của lộ trình **Junior DevOps / Platform Engineer** từ **12/10/2026 đến 05/02/2027**.

Mục tiêu cuối cùng không phải là học thuộc thật nhiều lệnh. Mục tiêu là có thể:

- giải thích được hệ thống hoạt động như thế nào;
- tự dựng lại hệ thống từ đầu;
- vận hành và quan sát được trạng thái của nó;
- tìm đúng nguyên nhân khi hệ thống lỗi;
- sửa lỗi, kiểm tra lại và rollback an toàn;
- trình bày kết quả bằng tài liệu và evidence rõ ràng.

Roadmap đầy đủ: [roadmap-devops-platform-mo-rong-gio-cong-ty-w3-w25.html](../roadmap-devops-platform-mo-rong-gio-cong-ty-w3-w25.html)

## Bắt đầu từ đâu?

Mỗi lần học, làm theo thứ tự sau:

1. Xác định tuần và domain đang học trong bảng tiến độ bên dưới.
2. Vào đúng thư mục chủ đề, đọc tài liệu trước khi làm lab.
3. Tự dự đoán kết quả trước khi chạy lệnh.
4. Dựng happy path và lưu lại baseline.
5. Tạo lỗi hoặc xử lý lỗi được giao.
6. Thu thập evidence ở ít nhất hai lớp, ví dụ Terraform plan và trạng thái Kubernetes.
7. Ghi nguyên nhân, cách sửa, cách kiểm tra và cách cleanup vào README của lab.
8. Chỉ đánh dấu hoàn thành khi đạt Definition of Done, không đánh dấu vì đã đọc xong.

Luồng học chuẩn:

```text
Cơ chế → Cấu hình → Triển khai → Quan sát → Tạo lỗi → Chẩn đoán → Sửa → Verify → Cleanup
```

## Cấu trúc workspace

```text
F/
├── README.md                 # Trang chủ và bảng tiến độ chung
├── linux/                    # Linux foundation và host operations
├── network/                  # Networking foundation và troubleshooting
├── AWS/                      # AWS manual labs và kiến trúc cloud
├── ansible/                  # Configuration management bằng Ansible
│   ├── docs/
│   └── ansible-jun/
└── terraform/                # Infrastructure as Code bằng Terraform
    ├── docs/
    ├── k8s-config/           # Kubeconfig cục bộ, không được commit public
    └── terraform-jun/
        ├── lab1/
        └── lab2/
```

Các thư mục sẽ bổ sung khi roadmap đi đến giai đoạn tương ứng:

```text
docker/                       # Container, image, Compose và runtime debug
kubernetes/                   # Workload, Service, Ingress, policy và debug
ci-cd/                        # Pipeline, registry, GitOps và Argo CD
observability/                # Metrics, logs, dashboard và alert
security/                     # Secret, IAM, RBAC và hardening
capstone/                     # Incident tổng hợp và báo cáo cuối khóa
portfolio/                    # Repo public-safe, CV và tài liệu phỏng vấn
```

Chỉ tạo thư mục mới khi bắt đầu học chủ đề đó. Không cần tạo trước toàn bộ cấu trúc.

## Vai trò của từng thư mục hiện tại

### `linux/`

Lưu nội dung về process, systemd, filesystem, permission, storage, package, log, shell, tài nguyên máy, host networking, SSH, security và recovery.

Một lab Linux hoàn chỉnh nên có:

- file cấu hình hoặc script đã viết;
- lệnh quan sát trạng thái;
- lỗi đã tạo hoặc gặp phải;
- nguyên nhân gốc;
- cách sửa và kết quả kiểm tra lại.

### `network/`

Lưu sơ đồ, cấu hình và packet capture cho Ethernet, ARP, IP/CIDR, VLAN, routing, DNS, TCP/UDP, HTTP/TLS, firewall, NAT, VPN và luồng mạng Kubernetes/cloud.

Mỗi bài nên trả lời được bốn câu hỏi:

1. Gói tin bắt đầu từ đâu?
2. Nó đi qua những lớp và thiết bị nào?
3. Đường về đi như thế nào?
4. Quan sát ở đâu để chứng minh kết luận?

### `AWS/`

Lưu các lab dựng thủ công IAM, VPC, EC2, EBS, ALB, RDS, S3, Route 53, ACM và CloudWatch. Giai đoạn này ưu tiên hiểu dịch vụ và luồng traffic trước khi tự động hóa bằng Terraform.

Mọi lab AWS phải có bước kiểm tra chi phí và cleanup. Không commit access key, secret key hoặc dữ liệu tài khoản.

### `ansible/`

Lưu inventory, playbook, role, template và tài liệu về configuration management.

Tiêu chí quan trọng nhất là tính lặp lại:

```text
Lần chạy đầu: hệ thống được cấu hình đúng
Lần chạy thứ hai: changed=0 nếu không có yêu cầu thay đổi
```

Điểm bắt đầu: [ANSIBLE-HANDBOOK-JUNIOR-DEVOPS.md](ansible/ansible-jun/ANSIBLE-HANDBOOK-JUNIOR-DEVOPS.md)

### `terraform/`

Lưu tài liệu Infrastructure as Code, các lab Terraform và kubeconfig dùng cho môi trường học cục bộ.

- Đọc trước: [Tổng quan Terraform](terraform/docs/terraform-overview.md)
- Ôn module và cấu trúc dự án: [Modules và cấu trúc dự án](terraform/docs/08-modules-va-cau-truc-du-an.md)
- Lab hiện tại: [Terraform Lab 2](terraform/terraform-jun/lab2/README.md)

Khi làm Terraform luôn đi theo chu trình:

```powershell
terraform fmt -recursive
terraform init
terraform validate
terraform plan
terraform apply
terraform output
terraform plan
```

Lệnh `terraform plan` cuối cùng phải cho biết **No changes** nếu không có drift ngoài dự kiến. Sau khi học xong hoặc trước khi đổi lab, cân nhắc `terraform destroy` để cleanup tài nguyên không còn dùng.

## Lịch học đến Tết

Roadmap chia thành 17 tuần, từ W3 đến W19. Các ô dưới đây là bảng theo dõi cấp cao; evidence chi tiết phải nằm trong README của từng lab.

| Xong | Tuần | Thời gian | Trọng tâm | Kết quả cần có |
|---|---|---|---|---|
| [ ] | W3 | 12–18/10/2026 | Linux core | Process, systemd, filesystem và permission; tự dựng service chạy bằng user riêng |
| [ ] | W4 | 19–25/10/2026 | Linux data & automation | Mount bền vững, package rollback, logrotate, timer và backup |
| [ ] | W5 | 26/10–01/11/2026 | Linux operations gate | Chẩn đoán CPU/memory/I/O/network, SSH, firewall và recovery |
| [ ] | W6 | 02–08/11/2026 | Network L2/L3 | Namespace, veth, bridge, ARP, CIDR và VLAN |
| [ ] | W7 | 09–15/11/2026 | Routing đến application | Route hai chiều, DNS, TCP/UDP, HTTP/TLS và reverse proxy |
| [ ] | W8 | 16–22/11/2026 | Network operations gate | Firewall, conntrack, NAT, MTU, VPN và network path của Kubernetes |
| [ ] | W9 | 23–29/11/2026 | Docker & Bash transfer | Non-root image, Compose app/DB và script chẩn đoán an toàn |
| [ ] | W10 | 30/11–06/12/2026 | AWS IAM & VPC | Guardrail, role/policy và VPC hai AZ dựng thủ công |
| [ ] | W11 | 07–13/12/2026 | AWS services | ALB → EC2 → RDS và EC2 role → S3 |
| [ ] | W12 | 14–20/12/2026 | AWS architecture & recovery | HTTPS, monitoring, backup/restore và architecture review |
| [ ] | W13 | 21–27/12/2026 | On-prem & Ansible | Hai VM và một HTTP service cấu hình idempotent bằng Ansible |
| [ ] | W14 | 28/12/2026–03/01/2027 | Terraform foundations | Resource graph, plan, state, backend, lock, import và module VPC |
| [ ] | W15 | 04–10/01/2027 | Terraform full stack | Terraform provision → Ansible configure → verify → destroy |
| [ ] | W16 | 11–17/01/2027 | CI/CD & Argo CD | Test, build, scan, push image, GitOps deploy và rollback |
| [ ] | W17 | 18–24/01/2027 | Observability & security | Dashboard, log correlation, alert, runbook, secret/IAM/RBAC review |
| [ ] | W18 | 25–31/01/2027 | Production incident capstone | Điều tra và phục hồi 12 incident đa lớp |
| [ ] | W19 | 01–05/02/2027 | Portfolio, CV & apply | Repo public-safe, walkthrough 5 phút, mock interview và CV |

Ngày **06/02/2027** là ngày nghỉ hoàn toàn theo roadmap.

## Các cổng năng lực bắt buộc

| Gate | Thời điểm | Điều kiện PASS tối thiểu |
|---|---|---|
| G-Linux | Cuối W5 | 8 fault phủ ít nhất 8/12 domain; xác định đúng ít nhất 7 và sửa được ít nhất 6 |
| G-Network | Cuối W8 | 10 incident phủ ít nhất 9/12 domain; tìm đúng root cause ít nhất 8 và fix/rollback ít nhất 7 |
| G-AWS | W12 | Dựng stack thủ công, restore và cleanup; kiểm riêng HTTP, DB và IAM |
| G-IaC | W15 | Cold apply → Ansible → verify → destroy; đọc được plan/state và tách lỗi IaC khỏi runtime |
| G-Ops | W18 | 12 incident đa lớp; xác định đúng ít nhất 10 và recover ít nhất 9 |
| G-Portfolio | W19 | Repo public-safe, walkthrough 5 phút, mock ít nhất 8/10 và gửi đơn ứng tuyển đầu tiên |

Không dùng các cách “chữa cháy mù” như `chmod 777`, reboot ngay hoặc restart liên tục mà chưa thu thập evidence.

## Khung làm việc cho mỗi lab

Mỗi lab nên có một `README.md` với cấu trúc tối thiểu sau:

```markdown
# Tên lab

## Mục tiêu
Sau lab này tôi phải tự làm và giải thích được điều gì?

## Kiến trúc / luồng hoạt động
Vẽ hoặc mô tả request, dependency và ranh giới hệ thống.

## Điều kiện đầu vào
Phiên bản công cụ, môi trường, credential hoặc file cấu hình cần có.

## Các bước thực hiện
Ghi lệnh quan trọng và giải thích mục đích, không chỉ chép toàn bộ terminal.

## Kiểm tra kết quả
Happy path, negative test và kết quả mong đợi.

## Sự cố và cách chẩn đoán
Symptom → giả thuyết → evidence → root cause → minimal fix.

## Cleanup
Cách xóa tài nguyên và xác nhận không còn sót lại.

## Bài học rút ra
Viết lại bằng lời của mình từ 3 đến 5 ý.
```

## Tiêu chuẩn evidence

Một kết luận kỹ thuật chỉ được coi là chắc chắn khi có bằng chứng phù hợp. Tùy bài, evidence có thể gồm:

- file cấu hình hoặc phần diff quan trọng;
- output của `systemctl`, `journalctl`, `ss`, `ip`, `dig` hoặc `tcpdump`;
- `terraform plan`, `terraform output` và tài nguyên thực tế;
- Ansible recap của lần chạy đầu và lần chạy thứ hai;
- Kubernetes events, logs, endpoint và rollout status;
- ảnh dashboard, alert timeline hoặc incident timeline;
- kết quả positive test và negative test;
- bằng chứng cleanup.

Không đưa password, token, private key, kubeconfig, Terraform state hoặc thông tin tài khoản thật vào evidence public.

## Quy tắc quản lý Git

- Mỗi thay đổi nên phục vụ một mục tiêu học rõ ràng.
- Commit sau khi lab đạt một checkpoint có thể chạy lại.
- Viết commit message mô tả kết quả, ví dụ `feat(terraform): complete lab2 application module`.
- Chạy secret scan hoặc tự kiểm tra credential trước khi push.
- Không commit `.terraform/`, `*.tfstate`, `*.tfstate.*`, kubeconfig, private key, `.env` hoặc file chứa secret.
- Nên commit `.terraform.lock.hcl` để các thành viên và pipeline dùng cùng phiên bản provider đã được chọn.
- Không sửa lịch sử Git chỉ để che một lỗi chưa hiểu; ghi lại lỗi và cách sửa trong lab.

Gợi ý `.gitignore` tối thiểu khi workspace được quản lý bằng Git:

```gitignore
**/.terraform/*
*.tfstate
*.tfstate.*
*.tfplan
*.pem
*.key
.env
terraform/k8s-config/*
```

Nếu cần giữ một file mẫu, tạo file không chứa secret như `.env.example`, `terraform.tfvars.example` hoặc `kubeconfig.example.yaml`.

## Nhịp học mỗi tuần

Quỹ thời gian mục tiêu:

- **10 giờ/tuần** từ W3 đến W18;
- **8 giờ** cho W19;
- **8–12 giờ linh hoạt tại công ty** nếu có, chỉ dùng để đào sâu hoặc làm task thật cùng domain;
- **30–60 phút tiếng Anh mỗi ngày** theo lịch riêng, không lấy vào block kỹ thuật.

Một tuần tiêu chuẩn:

| Buổi | Nội dung | Kết quả |
|---|---|---|
| S1 | Mechanism & config | Giải thích được causal chain và biết phải quan sát ở đâu |
| S2 | Guided deploy & observe | Happy path chạy, có baseline rõ ràng |
| S3 | Operate & break/fix | Tìm đúng layer và root cause trước khi sửa |
| S4 | Independent build | Tự dựng lại không nhìn walkthrough trong giai đoạn đầu |
| S5 | Gate & weekly review | Làm fault mù, chấm điểm và đặt lịch ôn lại |

Nếu trượt gate, buổi linh hoạt của tuần kế tiếp dùng để sửa điểm yếu. Không mở rộng sang chủ đề mới chỉ để cảm thấy mình đang tiến nhanh.

## Định nghĩa hoàn thành

Một chủ đề chỉ được đánh dấu hoàn thành khi có đủ chuỗi sau:

```text
Prediction
  → Baseline
  → One controlled change
  → Evidence ở ít nhất hai lớp
  → Giải thích quan hệ nhân quả
  → Minimal fix
  → Positive test + Negative test
  → Cleanup hoặc rollback
```

Đọc xong tài liệu, chạy theo tutorial hoặc thấy lệnh trả về exit code `0` chưa có nghĩa là đã hiểu và chưa đủ điều kiện PASS.

## Đích đến ngày 05/02/2027

Đến cuối roadmap, workspace này phải giúp chứng minh rằng người học có thể:

- tự dựng một stack on-prem hoặc AWS;
- tự động hóa provisioning bằng Terraform và configuration bằng Ansible;
- delivery ứng dụng qua CI/CD và Argo CD;
- quan sát metrics, logs, events và xử lý incident có phương pháp;
- bảo vệ secret, IAM, RBAC và network boundary ở mức phù hợp;
- cold rebuild, verify, rollback và cleanup;
- trình bày kiến trúc, quyết định kỹ thuật và incident bằng evidence;
- chuyển các lab tốt nhất thành portfolio public-safe.

README này là bản đồ chung. Kiến thức thật nằm trong những lab bạn có thể tự dựng lại, tự phá, tự sửa và tự giải thích.
