# L08 — Shell Safety & Bash Automation · Theory

## Phạm vi và nguồn

Phần cốt lõi đối chiếu [LPIC-1 Objectives V5.0 — LPI](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0):

- **103.1:** command line, environment và quoting.
- **103.3:** file management, globbing và `find`.
- **103.4:** stdin/stdout/stderr, pipe, redirect và `tee`/`xargs`.
- **105.1:** shell environment, profiles, functions và PATH.
- **105.2:** script đơn giản, loop, test, command substitution, exit status, `&&`, `||`, shebang và quyền thực thi.

## Thứ tự học

1. [Shell, command và environment](./01-shell-environment.md)
2. [Quoting, expansion và pathname an toàn](./02-quoting-expansion-safety.md)
3. [Exit status, điều kiện và pipeline](./03-exit-status-conditionals-pipelines.md)
4. [Input validation và file safety](./04-input-validation-file-safety.md)
5. [Script structure, cleanup và trap](./05-script-structure-cleanup.md)
6. [ShellCheck, debug và troubleshooting](./06-debugging-and-shellcheck.md)
7. [Command reference](./00-command-reference.md)

## Mô hình tư duy

```text
shell đọc command
      ↓
expansion/quoting/globbing
      ↓
program nhận argv + environment
      ↓
exit status + stdout/stderr
      ↓
script quyết định tiếp tục, dừng hoặc rollback
```

