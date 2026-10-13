# L01 — Environment Variables: Danh sách câu lệnh

File này là phần tra cứu command cho bài Environment Variables.

Phần lý thuyết nằm ở:

[06-environment.md](./06-environment.md)

---

## 1. Xem toàn bộ environment hiện tại

~~~bash
printenv
~~~

Hoặc:

~~~bash
env
~~~

Hai lệnh này in ra các environment variable của shell hiện tại.

---

## 2. Xem một biến cụ thể

~~~bash
printenv HOME
printenv PATH
printenv APP_ENV
~~~

Trong shell cũng có thể dùng:

~~~bash
echo "$HOME"
echo "$PATH"
echo "$APP_ENV"
~~~

Nếu biến không tồn tại, thường kết quả sẽ rỗng.

---

## 3. Tạo shell variable

~~~bash
DEMO_VAR="hello"
~~~

Kiểm tra trong shell hiện tại:

~~~bash
echo "$DEMO_VAR"
~~~

Tuy nhiên biến này chưa chắc được truyền xuống process con.

---

## 4. Export thành environment variable

~~~bash
export DEMO_ENV="hello-linux"
~~~

Kiểm tra:

~~~bash
printenv DEMO_ENV
~~~

Tạo child shell:

~~~bash
bash
~~~

Trong child shell:

~~~bash
echo "$DEMO_ENV"
~~~

Child shell nhìn thấy biến vì biến đã được export.

Thoát child shell:

~~~bash
exit
~~~

---

## 5. So sánh biến có export và không export

Tạo một biến bình thường:

~~~bash
DEMO_LOCAL="local-value"
~~~

Tạo một environment variable:

~~~bash
export DEMO_EXPORTED="exported-value"
~~~

Tạo child shell:

~~~bash
bash
~~~

Kiểm tra:

~~~bash
echo "$DEMO_LOCAL"
echo "$DEMO_EXPORTED"
~~~

Thông thường:

- DEMO_LOCAL không được truyền xuống child;
- DEMO_EXPORTED được truyền xuống child.

Thoát child shell:

~~~bash
exit
~~~

---

## 6. Truyền environment cho một command duy nhất

~~~bash
DEMO_TEMP="only-this-command" printenv DEMO_TEMP
~~~

Biến này chỉ được truyền cho command đó.

Kiểm tra sau khi command kết thúc:

~~~bash
printenv DEMO_TEMP
~~~

Thông thường sẽ không còn giá trị.

Mẫu tổng quát:

~~~bash
NAME=value command
~~~

Ví dụ:

~~~bash
APP_ENV=production python3 app.py
~~~

Ở đây APP_ENV được truyền vào process Python.

---

## 7. Xem environment của một process

Lấy PID của process:

~~~bash
PID=1234
~~~

Xem environment dạng raw:

~~~bash
cat /proc/$PID/environ
~~~

Vì các biến được ngăn cách bằng ký tự null, nên nên chuyển null thành newline:

~~~bash
tr '\0' '\n' < /proc/$PID/environ
~~~

Tìm một biến cụ thể:

~~~bash
tr '\0' '\n' < /proc/$PID/environ | grep '^APP_ENV='
~~~

Hoặc:

~~~bash
tr '\0' '\n' < /proc/$PID/environ | grep DEMO
~~~

Ý nghĩa:

> Đang quan sát environment runtime thực tế của process, không chỉ environment của shell hiện tại.

---

## 8. Xem environment bằng ps

Một số hệ thống hỗ trợ:

~~~bash
ps e -p "$PID"
~~~

Hoặc xem command cùng environment:

~~~bash
ps auxeww -p "$PID"
~~~

Proc/PID/environ thường rõ ràng hơn khi cần kiểm tra chính xác từng biến.

---

## 9. Tìm process theo command và kiểm tra environment

Tìm process theo command:

~~~bash
ps aux | grep python
~~~

Tốt hơn, dùng:

~~~bash
pgrep -a python
~~~

Xem environment của từng PID:

~~~bash
for PID in $(pgrep python); do
  echo "PID=$PID"
  tr '\0' '\n' < "/proc/$PID/environ" | grep '^APP_ENV='
done
~~~

---

## 10. Xóa environment variable

Xóa biến khỏi shell hiện tại:

~~~bash
unset DEMO_ENV
~~~

Kiểm tra:

~~~bash
printenv DEMO_ENV
~~~

Nếu không còn output, biến đã được xóa khỏi environment của shell hiện tại.

---

## 11. Environment trong Docker image lúc build

### Dùng build argument

Build image:

~~~bash
docker build \
  --build-arg VITE_API_URL=https://api.example.com \
  -t my-frontend .
~~~

Dockerfile:

~~~dockerfile
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build
~~~

Trong trường hợp frontend dùng Vite, các biến public thường phải có prefix VITE_.

Build-time variable thường được bundler ghi vào file JavaScript trong thư mục dist.

---

## 12. Kiểm tra ARG và ENV trong Dockerfile

Ví dụ Dockerfile:

~~~dockerfile
ARG BUILD_MODE=production
ENV APP_ENV=production

RUN echo "BUILD_MODE=$BUILD_MODE"
RUN echo "APP_ENV=$APP_ENV"
~~~

Build với giá trị khác:

~~~bash
docker build \
  --build-arg BUILD_MODE=staging \
  -t my-frontend .
~~~

Điểm cần phân biệt:

- ARG chủ yếu dùng trong lúc build;
- ENV có thể tồn tại trong image và container runtime;
- frontend static có thể đã ghi giá trị vào bundle trong lúc build.

---

## 13. Xem environment của image

~~~bash
docker image inspect my-frontend
~~~

Chỉ xem phần environment:

~~~bash
docker image inspect \
  --format '{{json .Config.Env}}' \
  my-frontend
~~~

---

## 14. Truyền environment khi chạy container

Truyền một biến:

~~~bash
docker run --rm \
  -e APP_ENV=production \
  my-frontend
~~~

Truyền nhiều biến:

~~~bash
docker run --rm \
  -e APP_ENV=production \
  -e API_URL=https://api.example.com \
  my-frontend
~~~

Truyền từ biến của shell:

~~~bash
export API_URL="https://api.example.com"

docker run --rm \
  -e API_URL \
  my-frontend
~~~

---

## 15. Dùng file environment với Docker

Tạo file .env.production:

~~~text
APP_ENV=production
API_URL=https://api.example.com
~~~

Chạy container:

~~~bash
docker run --rm \
  --env-file .env.production \
  my-frontend
~~~

Kiểm tra environment trong container:

~~~bash
docker run --rm \
  --env-file .env.production \
  my-frontend \
  env
~~~

Không commit file chứa secret vào Git.

---

## 16. Kiểm tra environment của container đang chạy

Liệt kê container:

~~~bash
docker ps
~~~

Xem environment trong metadata:

~~~bash
docker inspect \
  --format '{{range .Config.Env}}{{println .}}{{end}}' \
  <container-name-or-id>
~~~

Hoặc chạy command trong container:

~~~bash
docker exec <container-name-or-id> env
~~~

Tìm một biến:

~~~bash
docker exec <container-name-or-id> env | grep API_URL
~~~

---

## 17. Build-time và runtime: điểm dễ nhầm

### Build-time

~~~text
docker build
    ↓
npm run build
    ↓
static JavaScript bundle
~~~

Giá trị environment có thể bị ghi trực tiếp vào bundle.

### Runtime

~~~text
docker run -e API_URL=...
    ↓
process trong container nhận biến
~~~

Nếu container chỉ chạy nginx để phục vụ static files, browser không tự đọc được environment của nginx.

Muốn đổi cấu hình mà không rebuild image, cần runtime config:

~~~text
container start
    ↓
entrypoint đọc environment
    ↓
tạo config.js
    ↓
frontend đọc window.APP_CONFIG
~~~

---

## 18. Kiểm tra frontend có đang dùng build-time config không

Tìm URL trong thư mục build:

~~~bash
grep -R "api.example.com" dist/
~~~

Tìm tên biến:

~~~bash
grep -R "VITE_API_URL" dist/
~~~

Nếu giá trị xuất hiện trong JavaScript bundle, nó đã được đưa vào frontend build.

Giá trị trong frontend có thể bị người dùng xem. Không đưa secret vào frontend.

---

## 19. Checklist ghi nhớ

- export NAME=value: đưa biến vào environment của shell.
- NAME=value command: chỉ truyền biến cho command đó.
- /proc/PID/environ: xem environment runtime của process.
- ARG: biến chủ yếu dùng lúc Docker build.
- ENV: biến có thể tồn tại trong image hoặc container runtime.
- docker run -e: truyền biến lúc chạy container.
- --env-file: đọc nhiều biến từ file.
- Frontend static thường bake config vào bundle lúc build.
- Environment của nginx/container không tự động trở thành environment của browser.
- Secret không được đưa vào frontend bundle.

