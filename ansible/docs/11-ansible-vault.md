# 11. Secrets và Ansible Vault

> [← Quay lại mục lục](./README.md)

## Cách học chương này

Vault giải quyết việc mã hóa dữ liệu trong repository, không giải quyết toàn bộ secret lifecycle. Hãy phân biệt ciphertext, Vault password, CI variable và runtime secret.

## 1. Vì sao không commit plaintext?

Git giữ history. Xóa secret khỏi working tree không xóa chắc chắn khỏi commit cũ. Password/token trong inventory, template, debug hoặc diff có thể bị lộ cho người không cần quyền.

```text
Repository → ciphertext Vault
Control/CI → Vault password qua secret store
Managed node → nhận secret cần thiết, không nhận Vault password
```

## 2. Vault operations

```bash
ansible-vault create secrets/dev.yml
ansible-vault edit secrets/dev.yml
ansible-vault encrypt secrets/plain.yml
ansible-vault view secrets/dev.yml
```

File Vault thường bắt đầu bằng `$ANSIBLE_VAULT;`. Ciphertext có thể commit nếu policy cho phép; password không commit.

## 3. Không để secret lọt vào output

```yaml
- name: Create application credential
  ansible.builtin.user:
    name: appuser
    password: "{{ app_password }}"
  no_log: true
```

`no_log` cần đặt có chủ đích vì làm giảm khả năng debug. Không dùng `debug: var=app_password`; cẩn thận với `--diff`, exception và command stdout.

## Cấu trúc file

```text
inventories/dev/group_vars/
├── all.yml
└── vault.yml       # ciphertext
```

Ví dụ chỉ dùng placeholder:

```yaml
app_password: CHANGE_ME_IN_LOCAL_LAB
```

## Lệnh cần chạy

**Git Bash/WSL — control node:**

```bash
ansible-vault create inventories/dev/group_vars/vault.yml
ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --ask-vault-pass
```

Trong CI, dùng protected/masked variable hoặc secret manager; không echo variable và không tạo artifact chứa password file.

## Thực hành cuối chương: secret boundary

Tạo Vault file với giá trị giả, dùng nó trong task có `no_log`, rồi kiểm tra:

```bash
head -n 1 inventories/dev/group_vars/vault.yml
git grep -n -i 'password\|token\|private_key' -- ':!*.md'
```

Hoàn thành khi output không có plaintext secret và bạn giải thích được secret tồn tại ở đâu trong từng bước.

## Tài liệu chính thức

- [Using Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [Vault encrypted files](https://docs.ansible.com/ansible/latest/vault_guide/vault_using_encrypted_content.html)
- [Logging sensitive output](https://docs.ansible.com/ansible/latest/reference_appendices/logging.html)

