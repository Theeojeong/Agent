# Agent-KMMLU Project

본 저장소는 RAG 기반 에이전트 시스템을 구축하고, KMMLU Criminal-Law 테스트셋으로 성능을 평가하기 위한 코드와 환경을 제공합니다.

## 디렉터리 구조

```
├── docker/              # Dockerfile 보관 디렉터리
├── src/                 # 파이썬 소스 코드 (에이전트, 데이터 처리, 평가 등)
├── data/
│   ├── raw/             # RAG에 사용될 원본(raw) 데이터
│   └── processed/       # 정제·분할된 데이터 (벡터화 대상)
├── scripts/             # 실행 스크립트 (run_all.sh 등)
├── requirements.txt     # Python 의존성 목록
├── .gitignore
└── README.md            # 프로젝트 안내 문서
```

## 요구 사항

- OpenAI: 환경변수 `OPENAI_API_KEY` 필요
- 모델 제한: LLM=`gpt-4o-mini`, 임베딩=`text-embedding-small`
- 실행 시간: 인덱스 구축+배치 입력 생성은 1시간 내 완료 (배치 응답 대기 시간 제외)

## 빠른 시작

```bash
# 1. 도커 이미지 빌드 및 컨테이너 실행
$ # 루트에 .env 파일 생성 (예)
$ cat > .env << 'EOF'
$ OPENAI_API_KEY=sk-...
$ HF_TOKEN= # 선택 (프라이빗이면 설정)
$ EOF

$ # 도커 빌드 및 실행
$ docker compose -f docker/docker-compose.yml up --build

# 2. 컨테이너 내부에서 전체 파이프라인 실행 (데이터 다운로드 → 전처리 → 임베딩 → 평가)
$ ./scripts/run_all.sh
```

## 파이프라인 상세

1) 데이터 다운로드 (`src/download_data.py`)
- HF `KMMLU` Criminal-Law 테스트셋을 `data/raw/kmmlu_test.parquet` 로 저장
- `HAERAEHUB/KMMLU`와 `HAERAE-HUB/KMMLU`를 순차 시도

2) 지식베이스 구축 (`src/build_db.py`)
- `documents/형법(법률).pdf`, `documents/형사소송법(법률).pdf` 로드 → 청크 분할 → 임베딩(`text-embedding-small`) → Chroma 인덱스 저장(`data/processed/chroma`)

3) 배치 입력 생성 (`src/make_batch_input.py`)
- 각 문제에 대해 Top-3 관련 청크를 검색하여 컨텍스트와 함께 프롬프트 구성
- OpenAI Batch 입력 규격(JSONL) `batch_input.jsonl` 생성. 모델=`gpt-4o-mini`, temperature=0

4) 배치 제출 및 대기 (`src/submit_batch.py`)
- 입력 파일 업로드 → 배치 생성 → 완료까지 폴링 → `batch_output.jsonl` 저장

5) 평가 (`src/evaluate.py`)
- `batch_output.jsonl`에서 모델 응답의 선택지(A-D) 추출 → 정답과 비교 → 정확도 출력 및 `benchmark.txt` 저장

## 제출 가이드

- `benchmark.txt`, `batch_input.jsonl`, `batch_output.jsonl` 포함
- 전체 크기 2GB 이하 유지
- 재현 방법을 본 README에 명시

## 트러블슈팅

- 권한: 윈도우에서 실행 시 `scripts/run_all.sh` 실행권한은 Dockerfile에서 자동 처리
- 데이터셋 접근: 프라이빗 시 `HF_TOKEN` 필요
- 비용/시간: Batch API 대기 시간은 평가 시간에서 제외

---

> 작성: 2025-08-08, 업데이트: 2025-08-08

