# L03 — Command Reference: Filesystem & Path

## Tìm command

~~~bash
type -a COMMAND
command -v COMMAND
which COMMAND
whereis COMMAND
~~~

## Tìm file

~~~bash
find PATH -type f -name 'PATTERN'
find PATH -type f -iname 'PATTERN'
locate NAME
~~~

`find` quan sát filesystem hiện thời; `locate` tra database có thể cũ.

## Path và metadata

~~~bash
namei -l PATH
readlink PATH
readlink -f PATH
stat PATH
stat -c 'device=%d inode=%i links=%h type=%F name=%n' PATH
ls -li PATH
~~~

## File đang mở / open-unlinked

~~~bash
lsof PATH
lsof -p PID
lsof +L1
~~~

## Pseudo-filesystems

~~~bash
findmnt /proc
findmnt /sys
findmnt /dev
cat /proc/self/mounts
~~~

## Nguồn phạm vi LPIC

- [LPIC-1 Objectives V5.0 — 104.6/104.7](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [LPIC-1 Learning Material 101, Version 5.0](https://learning.lpi.org/pdfstore/LPI-Learning-Material-101-500-en.pdf)

