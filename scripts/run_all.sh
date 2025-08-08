#!/bin/bash

echo "🚀 KMMLU Criminal-Law 평가 파이프라인 시작"

# 1
echo "📥 데이터 다운로드 중"
python -m src.download_data

# 2
echo "🔧 KB 재구축 중"
python -m src.build_db

# 3
echo "📝 배치 입력 생성 중"
python -m src.make_batch_input

# 4
echo "🤖 배치 실행 중"
python -u -m src.submit_batch

# 5
echo "📊 평가 중"
python -m src.evaluate

echo "✅ 완료"
