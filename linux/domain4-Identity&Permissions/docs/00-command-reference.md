# L04 — Command Reference: Identity & Permissions

## Identity và accounts

~~~bash
id
id USER
groups
getent passwd USER
getent group GROUP
~~~

## Owner, group, mode

~~~bash
stat -c '%A %a %U:%G %u:%g %n' PATH
chmod 640 FILE
chmod u=rw,g=r,o= FILE
chown USER:GROUP PATH
chgrp GROUP PATH
~~~

## Umask và đường dẫn

~~~bash
umask
umask -S
namei -l PATH
~~~

## Sudo và ACL recognition

~~~bash
sudo -l
getfacl PATH
~~~

Chỉ chạy `chmod`, `chown`, `chgrp`, `umask` trong path/session lab phù hợp. Không thay đổi quyền hệ thống chỉ để “thử xem có hết lỗi không”.

## LPIC sources

- [LPIC-1 Objectives V5.0](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0): 104.5, 107.1, 110.1.
- [LPIC-1 Learning Material 101, Version 5.0](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf): 104.5.
- [LPIC-1 Learning Material 102, Version 5.0](https://learning.lpi.org/pdfstore/LPI-Learning-Material-102-500-en.pdf): 107.1.

