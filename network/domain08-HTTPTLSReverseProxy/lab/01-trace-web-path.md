# N08 Lab — Đọc đường đi HTTPS → proxy → hai backend

| | |
|---|---|
| **Thời lượng** | 90 phút |
| **Môi trường** | VM lab có `nginx`, `openssl`, `python3`, `curl`. Không chỉnh web production |
| **Mục tiêu** | Dựng TLS proxy → 2 backend, rồi tạo 2 lỗi (cert mismatch, backend down) và đọc đúng tầng lỗi |

```text
curl ──TLS(SNI app.lab)──► nginx 127.0.0.1:18443 ──► backend A 127.0.0.1:18081
                                                 └─► backend B 127.0.0.1:18082
```

> HAProxy được luyện kỹ ở [W7](../../weekly-labs/W7-routing-to-application.md)/W8. Lab này tập trung đọc tầng lỗi.

## Bước 0 — Backend và cert

```bash
mkdir -p ~/n08 && cd ~/n08
for x in A:18081 B:18082; do
  n=${x%%:*}; p=${x##*:}; mkdir -p $n && echo "backend $n" > $n/index.html && echo ok > $n/healthz
  (cd $n && python3 -m http.server $p --bind 127.0.0.1 >/dev/null 2>&1 &)
done
curl -s 127.0.0.1:18081/ ; curl -s 127.0.0.1:18082/

openssl req -x509 -newkey rsa:2048 -nodes -days 7 -subj "/CN=app.lab" \
  -addext "subjectAltName=DNS:app.lab" -keyout app.key -out app.crt
sudo mkdir -p /etc/nginx/n08 && sudo cp app.key app.crt /etc/nginx/n08/
```

## Bước 1 — Nginx

`/etc/nginx/conf.d/n08-lab.conf`:

```nginx
upstream n08_pool { server 127.0.0.1:18081; server 127.0.0.1:18082; }
server {
    listen 127.0.0.1:18443 ssl;
    server_name app.lab;
    ssl_certificate     /etc/nginx/n08/app.crt;
    ssl_certificate_key /etc/nginx/n08/app.key;
    access_log /var/log/nginx/n08-access.log;
    error_log  /var/log/nginx/n08-error.log;
    location / {
        proxy_pass http://n08_pool;
        proxy_set_header Host $host;
        proxy_connect_timeout 2s;
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
sudo ss -lntp | grep -E '1844|1808'
```

## Bước 2 — Positive path

```bash
C="--cacert $HOME/n08/app.crt --resolve app.lab:18443:127.0.0.1"
for i in 1 2 3 4; do curl -s $C https://app.lab:18443/; done   # A, B xen kẽ
curl -v $C https://app.lab:18443/healthz 2>&1 | grep -E 'Trying|SSL connection|subject|< HTTP'
```

Đánh dấu trong output: dòng nào là TCP, TLS, cert, HTTP.

## Bước 3 — Lỗi 1: cert mismatch

**Dự đoán** trước: client thấy gì? `n08-access.log` có dòng mới không?

```bash
curl -v --cacert ~/n08/app.crt --resolve other.lab:18443:127.0.0.1 https://other.lab:18443/
sudo tail -2 /var/log/nginx/n08-access.log
```

**Kết quả mong đợi:** lỗi `no alternative certificate subject name matches` (curl 60); access log **không** có request mới.

## Bước 4 — Lỗi 2: một backend down, rồi cả hai

```bash
pkill -f 'http.server 18082'
for i in 1 2 3 4; do curl -s -o /dev/null -w '%{http_code} ' $C https://app.lab:18443/; done; echo
sudo tail -3 /var/log/nginx/n08-error.log
```

**Kết quả mong đợi:** vẫn `200` (Nginx thử server kế tiếp — *passive* failover); error log có `connect() failed (111: Connection refused) ... upstream: "http://127.0.0.1:18082/"`.

```bash
pkill -f 'http.server 18081'
curl -s -o /dev/null -w '%{http_code}\n' $C https://app.lab:18443/    # 502
```

So sánh: 502 này khác 404 thế nào? Tạo 404: khởi động lại A, B rồi `curl $C https://app.lab:18443/khong-co`.

---

## Definition of Done

- [ ] Sơ đồ client → TLS proxy → A/B với port.
- [ ] Positive: thấy A/B xen kẽ; chú thích `curl -v` theo bước.
- [ ] Cert mismatch: dự đoán + client error + access log trống.
- [ ] Backend down: error log nginx + status 200 (một down) / 502 (cả hai).
- [ ] Bảng phân biệt TLS error / 502 / 404: ai tạo, log ở đâu.

## Cleanup

```bash
pkill -f 'http.server 1808'
sudo rm /etc/nginx/conf.d/n08-lab.conf && sudo rm -r /etc/nginx/n08
sudo nginx -t && sudo systemctl reload nginx
rm -r ~/n08
```
