#!/bin/bash

# 나비얌 챗봇 API 테스트 스크립트

# 설정
BASE_URL="${1:-http://localhost:8000}"  # 첫 번째 인자로 URL 받기, 기본값은 localhost

echo "🧪 나비얌 챗봇 API 테스트 시작"
echo "📡 테스트 URL: $BASE_URL"
echo

# 1. 헬스체크
echo "1️⃣ 헬스체크 테스트..."
curl -s "$BASE_URL/health" | jq '.' || echo "jq가 설치되지 않았습니다. raw 출력:"
curl -s "$BASE_URL/health"
echo -e "\n"

# 2. 루트 엔드포인트
echo "2️⃣ 루트 엔드포인트 테스트..."
curl -s "$BASE_URL/" | jq '.' 2>/dev/null || curl -s "$BASE_URL/"
echo -e "\n"

# 3. 챗봇 테스트 - 인사
echo "3️⃣ 챗봇 인사 테스트..."
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요", "user_id": "test_user"}' | \
  jq '.' 2>/dev/null || curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요", "user_id": "test_user"}'
echo -e "\n"

# 4. 챗봇 테스트 - 음식 요청
echo "4️⃣ 챗봇 음식 추천 테스트..."
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "치킨 먹고 싶어", "user_id": "test_user"}' | \
  jq '.' 2>/dev/null || curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "치킨 먹고 싶어", "user_id": "test_user"}'
echo -e "\n"

# 5. 챗봇 테스트 - 예산 문의
echo "5️⃣ 챗봇 예산 문의 테스트..."
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "1만원으로 뭐 먹을까", "user_id": "test_user"}' | \
  jq '.' 2>/dev/null || curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "1만원으로 뭐 먹을까", "user_id": "test_user"}'
echo -e "\n"

echo "✅ API 테스트 완료!"
echo "📚 더 자세한 API 문서: $BASE_URL/docs"