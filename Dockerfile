# мультистейдж сборка
FROM python:3.13-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

COPY requirements.txt .

RUN ln -s /usr/local/bin/python /usr/bin/python \
    && /usr/bin/python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p /build/media

# дистролесс образ для безопасности
FROM gcr.io/distroless/python3-debian13:nonroot

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder --chown=nonroot:nonroot /opt/venv /opt/venv
COPY --from=builder --chown=nonroot:nonroot /build /app

EXPOSE 8000

# извините, очень хотелось...
HEALTHCHECK --interval=30s \
    --timeout=3s \
    --start-period=10s \
    --retries=3 \
    CMD ["/opt/venv/bin/python", "-c", "import socket; s=socket.create_connection(('127.0.0.1', 8000), timeout=2); s.close()"]

ENTRYPOINT ["/opt/venv/bin/python"]

# пока без gunicorn
CMD ["manage.py", "runserver", "0.0.0.0:8000"]