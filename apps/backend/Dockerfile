# syntax=docker/dockerfile:1.7
FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=180 \
    PIP_RETRIES=10 \
    PIP_PROGRESS_BAR=off

WORKDIR /app
COPY requirements.txt .

# (optional) upgrade pip to get better retry behavior
RUN python -m pip install --upgrade pip

# ↑ Prefer prebuilt wheels, retry more, longer timeout
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary --default-timeout=180 --retries 10 -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000","--reload"]
