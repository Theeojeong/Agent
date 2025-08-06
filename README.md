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
├── logs/                # 실행 중 생성되는 로그 파일
├── requirements.txt     # Python 의존성 목록
├── .gitignore
└── README.md            # 프로젝트 안내 문서
```

## 빠른 시작

```bash
# 1. 도커 이미지 빌드 및 컨테이너 실행
$ docker compose -f docker/docker-compose.yml up --build

# 2. 컨테이너 내부에서 전체 파이프라인 실행 (데이터 다운로드 → 전처리 → 임베딩 → 평가)
$ ./scripts/run_all.sh
```

자세한 설명 및 옵션은 추후 섹션을 통해 추가될 예정입니다.

---

> 작성: 2025-08-06

