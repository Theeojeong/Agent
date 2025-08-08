FROM python:3.11-slim

# 1. 필수 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential ca-certificates dos2unix && \
    rm -rf /var/lib/apt/lists/*

# 2. 코드 복사
WORKDIR /app
COPY . .

# 3. CRLF 제거 + 실행 권한 부여
RUN find /app/scripts -type f -name "*.sh" -exec dos2unix {} + \
 && chmod +x /app/scripts/*.sh

# 4. 환경변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 5. 기본 실행
ENTRYPOINT ["bash", "scripts/run_all.sh"]