#!/bin/bash

# 나비얌 챗봇 GCP 배포 스크립트

set -e

# 색깔 출력 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정 변수
PROJECT_ID="${PROJECT_ID:-your-project-id}"
REGION="asia-northeast3"
SERVICE_NAME="naviyam-chatbot"
REPOSITORY_NAME="naviyam-repo"

echo -e "${BLUE}🚀 나비얌 챗봇 GCP 배포 시작${NC}"

# 1. 프로젝트 설정 확인
echo -e "${YELLOW}📋 프로젝트 설정 확인...${NC}"
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -e "${RED}❌ PROJECT_ID를 설정해주세요!${NC}"
    echo "export PROJECT_ID=your-actual-project-id"
    exit 1
fi

gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ 프로젝트: $PROJECT_ID${NC}"

# 2. 필요한 API 활성화
echo -e "${YELLOW}🔧 필요한 API 활성화...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
echo -e "${GREEN}✅ API 활성화 완료${NC}"

# 3. Artifact Registry 레포지토리 생성
echo -e "${YELLOW}📦 Artifact Registry 레포지토리 생성...${NC}"
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="나비얌 챗봇 Docker 이미지 저장소" || echo "레포지토리가 이미 존재합니다."
echo -e "${GREEN}✅ Artifact Registry 준비 완료${NC}"

# 4. Docker 인증 설정
echo -e "${YELLOW}🔑 Docker 인증 설정...${NC}"
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
echo -e "${GREEN}✅ Docker 인증 완료${NC}"

# 5. Cloud Build로 빌드 및 배포
echo -e "${YELLOW}🏗️  Cloud Build 시작...${NC}"
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_PROJECT_ID=$PROJECT_ID \
    .
    
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 빌드 및 배포 성공!${NC}"
else
    echo -e "${RED}❌ 빌드 또는 배포 실패${NC}"
    exit 1
fi

# 6. 서비스 URL 확인
echo -e "${YELLOW}🌐 서비스 URL 확인...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}✅ 배포 완료!${NC}"
    echo -e "${BLUE}📱 서비스 URL: $SERVICE_URL${NC}"
    echo -e "${BLUE}🔍 헬스체크: $SERVICE_URL/health${NC}"
    echo -e "${BLUE}💬 챗봇 테스트: $SERVICE_URL/chat${NC}"
    echo -e "${BLUE}📚 API 문서: $SERVICE_URL/docs${NC}"
else
    echo -e "${RED}❌ 서비스 URL을 찾을 수 없습니다.${NC}"
    exit 1
fi

# 7. 간단한 헬스체크
echo -e "${YELLOW}🩺 헬스체크 테스트...${NC}"
sleep 10  # 서비스가 준비될 시간을 줌

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health")
if [ "$HTTP_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ 헬스체크 성공! 서비스가 정상 동작 중입니다.${NC}"
else
    echo -e "${YELLOW}⚠️  헬스체크 응답: $HTTP_STATUS (서비스가 아직 시작 중일 수 있습니다)${NC}"
fi

echo -e "${BLUE}🎉 나비얌 챗봇 배포 완료!${NC}"