# 나비얌 (Naviyam) 챗봇 🍗

어린이를 위한 한국어 AI 챗봇 시스템 - "착한가게" 추천에 특화된 대화형 AI

## 🚀 빠른 시작

### 로컬 환경에서 실행

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 테스트 서버 실행
python test_simple_server.py

# 4. API 테스트
./test_api.sh
```

### Docker로 실행

```bash
# 1. Docker 이미지 빌드
docker build -f Dockerfile.simple -t naviyam-chatbot:simple .

# 2. 컨테이너 실행
docker run -p 8080:8000 naviyam-chatbot:simple

# 3. API 테스트
./test_api.sh http://localhost:8080
```

## 🌐 Google Cloud Platform 배포

### 사전 준비

1. GCP 프로젝트 생성
2. gcloud CLI 설치 및 인증
3. 프로젝트 ID 환경 변수 설정

```bash
export PROJECT_ID=your-actual-project-id
gcloud config set project $PROJECT_ID
gcloud auth login
```

### 자동 배포 (권장)

```bash
# 배포 스크립트 실행
./deploy.sh
```

### 수동 배포

```bash
# 1. 필요한 API 활성화
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# 2. Artifact Registry 생성
gcloud artifacts repositories create naviyam-repo \
    --repository-format=docker \
    --location=asia-northeast3

# 3. Docker 인증
gcloud auth configure-docker asia-northeast3-docker.pkg.dev

# 4. Cloud Build로 배포
gcloud builds submit --config=cloudbuild.yaml
```

## 📡 API 엔드포인트

### 기본 엔드포인트

- `GET /` - 루트 정보
- `GET /health` - 헬스체크
- `GET /docs` - Swagger UI API 문서

### 챗봇 엔드포인트

- `POST /chat` - 챗봇 대화

#### 요청 예시

```json
{
  "message": "치킨 먹고 싶어",
  "user_id": "test_user"
}
```

#### 응답 예시

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

## 🧪 테스트

### API 테스트

```bash
# 로컬 테스트
./test_api.sh

# 배포된 서비스 테스트
./test_api.sh https://your-service-url
```

### 직접 테스트

```bash
# 헬스체크
curl http://localhost:8000/health

# 챗봇 대화
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요", "user_id": "test"}'
```

## 🏗️ 프로젝트 구조

```
chat_bot_recomm/
├── test_simple_server.py    # 간단한 테스트 서버
├── requirements.txt         # Python 의존성
├── Dockerfile.simple       # Docker 설정 (간단 버전)
├── cloudbuild.yaml         # Cloud Build 설정
├── service.yaml            # Cloud Run 서비스 설정
├── deploy.sh               # 자동 배포 스크립트
├── test_api.sh             # API 테스트 스크립트
└── README.md               # 이 파일
```

## 🔧 설정

### 환경 변수

- `PORT`: 서버 포트 (기본값: 8000)
- `PROJECT_ID`: GCP 프로젝트 ID
- `PYTHONUNBUFFERED`: Python 출력 버퍼링 비활성화

### Cloud Run 설정

- **CPU**: 1 vCPU
- **메모리**: 2Gi
- **동시성**: 80 요청
- **타임아웃**: 300초
- **자동 스케일링**: 0-10 인스턴스

## 🐛 디버깅

### 로그 확인

```bash
# Cloud Run 로그
gcloud logs read --service=naviyam-chatbot --region=asia-northeast3

# 로컬 Docker 로그
docker logs <container-id>
```

### 일반적인 문제

1. **포트 충돌**: 8000 포트가 사용 중인 경우
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **Docker 빌드 실패**: 캐시 문제인 경우
   ```bash
   docker build --no-cache -f Dockerfile.simple -t naviyam-chatbot:simple .
   ```

3. **GCP 권한 문제**: 필요한 권한 확인
   ```bash
   gcloud projects get-iam-policy $PROJECT_ID
   ```

## 📋 할 일 목록

- [x] 기본 FastAPI 서버 구축
- [x] Docker 컨테이너화
- [x] GCP Cloud Run 배포 설정
- [ ] 실제 ML 모델 통합
- [ ] 사용자 인증 시스템
- [ ] 데이터베이스 연동
- [ ] 모니터링 및 로깅 개선

## 🤝 기여하기

1. Fork 프로젝트
2. Feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙋‍♂️ 지원

문제가 있으시면 이슈를 생성해주세요!

---

Made with ❤️ by Naviyam Team