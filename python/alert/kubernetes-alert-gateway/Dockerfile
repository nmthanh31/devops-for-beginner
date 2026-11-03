FROM python:3.15.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd \
    --create-home \
    --uid 10001 \
    appuser

COPY pyproject.toml ./

COPY src ./src

RUN python -m pip install --upgrade pip
RUN python -m pip install .

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "kubernetes_alert_gateway.main:app","--host","0.0.0.0","--port","8000"]