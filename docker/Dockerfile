FROM python:3.11-slim

# 1. 필수 패키지
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential ca-certificates dos2unix && \
    rm -rf /var/lib/apt/lists/*

# 2. 작업 디렉터리
WORKDIR /app

# 3. requirements 먼저 복사-설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 나머지 코드 복사
COPY . .

# 5. 스크립트 CRLF 제거 & 실행권한
RUN find /app/scripts -type f -name "*.sh" -exec dos2unix {} + \
 && chmod +x /app/scripts/*.sh

# 6. 환경변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 7. 기본 실행
ENTRYPOINT ["bash", "scripts/run_all.sh"]