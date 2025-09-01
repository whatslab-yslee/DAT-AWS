# Stage 1: 빌드 및 종속성 설치를 위한 베이스 스테이지
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim as python-base

# apt-packages.txt에 명시된 시스템 패키지 설치
COPY apt-packages.txt /tmp/apt-packages.txt
RUN apt-get update && \
    xargs -a /tmp/apt-packages.txt apt-get install -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 바이트코드(.pyc) 생성 활성화
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

# pyproject.toml를 복사하고 uv로 패키지 설치
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

# Stage 2: 최종 실행을 위한 애플리케이션 이미지
FROM python-base

WORKDIR /app

# 소스 코드 및 설정 복사
COPY . /app

# 기본 Nginx 설정 제거
RUN rm -f /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default

# 커스텀 Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 80 8000 8501

CMD ["supervisord", "-c", "supervisord.conf"]
