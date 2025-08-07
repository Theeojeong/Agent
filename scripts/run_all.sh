#!/bin/bash

echo "🚀 KMMLU Criminal-Law 평가 파이프라인 시작"

# 1
echo "📥 데이터 다운로드 중"
python src/download_data.py

# 2
echo "🔧 KB 재구축 중"
python src/langchain.py

# 3
echo "📝 배치 입력 생성 중"
python src/make_batch_input.py

# 4
echo "🤖 배치 실행 중"
python src/submit_batch.py

# 5
echo "📊 평가 중"
python src/evaluate.py

echo "✅ 완료"
