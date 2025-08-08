## 빠른 시작
```bash
# 1. .env 환경변수 설정 (호스트)
$ export OPENAI_API_KEY="sk-..."

# 2. 이미지 빌드 & 파이프라인 실행 (batch api 응답시간 약 30-40 분)
$ docker compose -f docker/docker-compose.yml up --build

# 3. 실행 로그가 다음 단계를 순차적으로 출력
1. 데이터 다운로드 중(KMMLU test parquet 저장)

2. dB 구축 중(PDF → 임베딩 → Chroma 인덱스)

3. 배치 입력 생성 중(batch_input.jsonl 작성)

4. 배치 실행 중(OpenAI Batch 제출·대기)

5. 평가 중(batch_output.jsonl → 정확도 계산)

6. 완료
```


## 결과 파일
1.  `batch_input.jsonl`: Batch API 입력 200 행

2.  `batch_output.jsonl`: Batch 결과 

3.  `benchmark.txt`: KMMLU Criminal-Law 정확도

4.  `data/processed/chroma/`: Chroma 벡터 인덱스


## 주요 스크립트
1. `src/download_data.py`: KMMLU test 셋 다운로드 → parquet 저장 

2. `src/build_db.py`: PDF 로드 → 청크 분할 → 임베딩(text-embedding-3-small) → Chroma 저장 

3. `src/make_batch_input.py`: RAG 컨텍스트를 포함한 Batch 입력 생성 

4. `src/submit_batch.py`: Batch API 제출·완료 대기·결과 파일 저장 

5. `src/evaluate.py`: 정답 매핑 후 정확도 계산 


## 커스터마이즈
* 청크 크기 / 겹침 길이 → `src/build_db.py` 파일의 `chunk_size`, `chunk_overlap` 변수

* 검색 문서 수(k) → `src/make_batch_input.py` 파일의 `retriever = ... search_kwargs=
{"k": 5}`

* 프롬프트 템플릿 → `make_batch_input.py` 파일의 `make_prompt()` 함수


## 요구 사항
* Docker ≥ 24, Docker Compose v2
* OpenAI API Key     → 환경변수 `OPENAI_API_KEY`
* PDF 원문 `documents/형법(법률).pdf`, `documents/형사소송법(법률).pdf` 준비 有


## 디렉터리 구조
```
├── docker/               # Dockerfile 컨테이너 정의
├── data/
│   ├── raw/              # KMMLU parquet, 원본 PDF 입력 데이터
│   └── processed/        # 청크 JSONL, Chroma 인덱스
├── scripts/              # 실행 스크립트 (run_all.sh)
├── src/                  # 파이프라인 소스 코드
├── docker-compose.yml    # 루트 위치 compose 파일
├── requirements.txt      # Python 의존성
└── README.md
```


---
*작성 2025-08-08*