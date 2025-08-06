FROM python:3.11-slim

# 1) 필수 패키지
RUN apt-get update && apt-get install -y build-essential

# 2) 코드 복사
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 3) 기본 실행: 전체 파이프라인
ENTRYPOINT ["bash", "scripts/run_all.sh"]
