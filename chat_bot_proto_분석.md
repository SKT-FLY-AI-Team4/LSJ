# 나비얌(Naviyam) 챗봇 프로젝트 분석

## 📋 프로젝트 개요

**나비얌**은 어린이를 위한 한국어 AI 챗봇 시스템으로, "착한가게" 추천에 특화된 대화형 AI입니다.

### 🎯 주요 기능
- 음식점 추천 (치킨, 피자 등)
- 예산 기반 맛집 추천
- 자연어 대화 인터페이스
- RESTful API 제공

## 🏗️ 프로젝트 구조

```
chat_bot_proto-main/
├── 📱 앱/서버
│   ├── main.py                      # 메인 FastAPI 서버
│   ├── test_simple_server.py        # 간단한 테스트 서버
│   └── api/                         # API 관련 모듈
│
├── 🧠 AI/ML 모델
│   ├── models/                      # AI 모델 (KoAlpaca, AX 모델)
│   ├── training/                    # 모델 학습 관련
│   └── inference/                   # 추론 엔진
│
├── 🔍 검색/추천
│   ├── rag/                         # RAG (검색 증강 생성)
│   ├── recommendation/              # 추천 시스템
│   └── nlp/                         # 자연어 처리
│
├── 📊 데이터 처리
│   ├── data/                        # 데이터 로더 및 전처리
│   └── nutrition/                   # 영양 정보 API
│
├── 🧪 테스트
│   ├── test_*.py                    # 다양한 테스트 파일들
│   └── tests/                       # 테스트 디렉토리
│
└── 🚀 배포
    ├── Dockerfile.simple            # Docker 설정
    ├── cloudbuild.yaml             # GCP Cloud Build
    └── deploy.sh                   # 배포 스크립트
```

## 🧪 테스트 방법

### 1️⃣ 빠른 테스트 (추천)

```bash
# 프로젝트 디렉토리로 이동
cd /Volumes/samsd/skt_teamproject/publicproject/chat_bot_proto/chat_bot_proto-main

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 기본 의존성만 설치 (빠른 테스트용)
pip install fastapi uvicorn pydantic

# 간단한 테스트 서버 실행
python3 test_simple_server.py
```

**다른 터미널에서 API 테스트:**
```bash
# API 테스트 스크립트 실행
./test_api.sh

# 또는 수동 테스트
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "치킨 먹고 싶어", "user_id": "test"}'
```

### 2️⃣ 전체 기능 테스트

```bash
# 전체 의존성 설치 (시간 소요)
pip install -r requirements.txt

# 메인 서버 실행 
python3 main.py
```

### 3️⃣ 개별 컴포넌트 테스트

```bash
# RAG 시스템 테스트
python3 test_rag_simple.py

# 벡터 검색 (FAISS) 테스트
python3 test_faiss_simple.py

# 영양 정보 API 테스트
python3 test_nutrition_api.py

# 성능 테스트
python3 test_phase3_performance.py
```

## 🔧 기술 스택

### 백엔드
- **FastAPI**: 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **Pydantic**: 데이터 검증

### AI/ML
- **PyTorch**: 딥러닝 프레임워크
- **Transformers**: Hugging Face 라이브러리
- **Sentence-Transformers**: 문장 임베딩
- **PEFT/LoRA**: 효율적인 파인튜닝

### 검색/벡터DB
- **FAISS**: 벡터 유사도 검색
- **ChromaDB**: 벡터 데이터베이스

### 데이터 처리
- **Pandas**: 데이터 조작
- **NumPy**: 수치 연산
- **scikit-learn**: 머신러닝 유틸리티

### 클라우드/배포
- **Google Cloud Platform**: 클라우드 플랫폼
- **Cloud Run**: 서버리스 컨테이너
- **Docker**: 컨테이너화

## 📡 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 | 예시 |
|-----------|-------|------|------|
| `/` | GET | 루트 정보 | 서버 상태 확인 |
| `/health` | GET | 헬스체크 | 서비스 상태 모니터링 |
| `/docs` | GET | API 문서 | Swagger UI |
| `/chat` | POST | 챗봇 대화 | 메시지 전송 및 응답 |

### 챗봇 API 사용 예시

**요청:**
```json
{
  "message": "치킨 먹고 싶어",
  "user_id": "test_user"
}
```

**응답:**
```json
{
  "response": "🍗 치킨이 먹고 싶으시군요! 근처 착한가게 치킨집을 찾아드릴게요.",
  "user_id": "test_user", 
  "timestamp": "2025-07-31T11:05:40.455360",
  "recommendations": [
    "BBQ치킨 (착한가게)",
    "교촌치킨 (할인가게)", 
    "네네치킨 (깨끗한가게)"
  ]
}
```

## 🚀 배포 방법

### 로컬 Docker 실행
```bash
# Docker 이미지 빌드
docker build -f Dockerfile.simple -t naviyam-chatbot:simple .

# 컨테이너 실행
docker run -p 8080:8000 naviyam-chatbot:simple
```

### GCP Cloud Run 배포
```bash
# 자동 배포 (권장)
./deploy.sh

# 수동 배포
gcloud builds submit --config=cloudbuild.yaml
```

## 🔍 주요 특징

### 1. 모듈러 아키텍처
- 각 기능별로 독립적인 모듈 구성
- 테스트 및 유지보수 용이

### 2. 다단계 테스트 시스템
- 간단한 기능 테스트부터 전체 통합 테스트까지
- 15개 이상의 다양한 테스트 스크립트

### 3. 확장 가능한 추천 시스템
- 협업 필터링, 콘텐츠 기반, 인기도 등 다중 전략
- RAG 기반 컨텍스트 인식

### 4. 클라우드 네이티브
- Docker 컨테이너화
- GCP Cloud Run 배포 지원
- 자동 스케일링

## 📈 개발 상태

### ✅ 완료된 기능
- [x] 기본 FastAPI 서버 구축
- [x] Docker 컨테이너화  
- [x] GCP Cloud Run 배포 설정
- [x] 기본 챗봇 대화 기능
- [x] API 테스트 자동화

### 🚧 개발 중인 기능
- [ ] 실제 ML 모델 통합
- [ ] 사용자 인증 시스템
- [ ] 데이터베이스 연동
- [ ] 모니터링 및 로깅 개선

## 💡 사용 권장사항

1. **개발/테스트**: `test_simple_server.py` 사용
2. **프로덕션**: `main.py` 또는 Docker 배포
3. **CI/CD**: `test_api.sh` 스크립트 활용
4. **모니터링**: `/health` 엔드포인트 사용

---

**Made with ❤️ by Naviyam Team**