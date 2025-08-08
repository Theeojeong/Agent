FROM python:3.11-slim

# 1) 필수 패키지
RUN apt-get update && apt-get install -y build-essential

# 2) 코드 복사
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CRLF 제거 & 실행권한 부여 (윈도우에서 체크아웃된 경우 대비)
RUN sed -i 's/\r$//' scripts/run_all.sh && chmod +x scripts/run_all.sh

# 3) 기본 실행: 전체 파이프라인
ENTRYPOINT ["bash", "scripts/run_all.sh"]


ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
