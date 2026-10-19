# 14. GitLab CI cho Ansible

> [← Quay lại mục lục](./README.md)

## Cách học chương này

CI chỉ đáng tin khi bạn hiểu runner đang chạy ở đâu, có network gì, dùng inventory nào và credential nào. Đừng bắt đầu từ YAML pipeline; bắt đầu từ execution environment của runner.

## 1. Pipeline model

```text
validate → syntax → lint → check-dev → deploy-dev → deploy-stag (manual)
```

CI runner có thể là control node tạm thời. Nó cần Ansible, collections, SSH client, known_hosts đúng và route tới managed nodes. Runner không tự có quyền SSH chỉ vì pipeline nằm trong GitLab.

## 2. Credentials

```text
GitLab protected/masked variables
        ├── SSH private key (tạm thời trong job)
        └── Vault password (không echo)
```

Private key phải có permission phù hợp và không đi vào artifact. Vault password không hard-code trong `.gitlab-ci.yml`. Host key verification nên được quản lý bằng known_hosts tin cậy, không tắt bừa bằng `StrictHostKeyChecking=no`.

## 3. Job boundaries

```yaml
stages: [validate, test, deploy]

syntax:
  stage: validate
  script:
    - yamllint .
    - ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --syntax-check

check_dev:
  stage: test
  script:
    - ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --check

deploy_stag:
  stage: deploy
  when: manual
  script:
    - ansible-playbook -i inventories/stag/hosts.yml playbooks/site.yml
```

Đây là skeleton; image, dependency install, runner tag, protected environment và credential setup phải phù hợp lab.

## Thực hành cuối chương: pipeline có điểm dừng

Tạo pipeline có validation, syntax, lint, check dev, deploy dev và manual staging. Làm một MR cố ý sai YAML/lint để quan sát job fail ở tầng nào. Chỉ cho staging chạy sau khi check/dev test pass.

## Tài liệu chính thức

- [GitLab CI YAML syntax](https://docs.gitlab.com/ci/yaml/)
- [GitLab protected variables](https://docs.gitlab.com/ci/variables/)
- [Ansible Vault in CI](https://docs.ansible.com/ansible/latest/vault_guide/vault_using_encrypted_content.html)

