#!/usr/bin/env bash
set -e

echo "=== 1. 데이터 다운로드 ==="
python src/download_data.py

echo "=== 2. KB 구축 (임베딩) ==="
python src/build_kb.py

echo "=== 3. 배치 입력 생성 ==="
python src/make_batch_input.py

echo "=== 4. OpenAI Batch 호출 ==="
python src/submit_batch.py         # 위 create_and_wait 스크립트

echo "=== 5. 정확도 계산 ==="
python src/evaluate.py

echo "모든 과정 완료"
