#!/usr/bin/env python3
"""
간단한 테스트 서버 - ML 패키지 없이 기본 FastAPI 동작 확인
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="나비얌 챗봇 테스트 API",
    description="기본 동작 확인용 테스트 서버",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "guest"

class ChatResponse(BaseModel):
    response: str
    user_id: str
    timestamp: str
    recommendations: List[str] = []

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

@app.get("/", response_model=HealthResponse)
async def root():
    """루트 엔드포인트"""
    return HealthResponse(
        status="healthy",
        message="나비얌 챗봇 테스트 서버가 정상 동작 중입니다!",
        version="0.1.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스체크 엔드포인트"""
    return HealthResponse(
        status="healthy", 
        message="OK",
        version="0.1.0"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 엔드포인트 - 간단한 mock 응답"""
    from datetime import datetime
    
    # 간단한 키워드 기반 응답
    message = request.message.lower()
    
    if "치킨" in message:
        response = "🍗 치킨이 먹고 싶으시군요! 근처 착한가게 치킨집을 찾아드릴게요."
        recommendations = ["BBQ치킨 (착한가게)", "교촌치킨 (할인가게)", "네네치킨 (깨끗한가게)"]
    elif "피자" in message:
        response = "🍕 피자가 땡기시는군요! 맛있는 피자집을 추천해드려요."
        recommendations = ["도미노피자 (할인중)", "피자헛 (가족세트)", "파파존스 (신선한재료)"]
    elif "안녕" in message or "hello" in message:
        response = "안녕하세요! 👋 나비얌 챗봇입니다. 어떤 음식이 드시고 싶으신가요?"
        recommendations = []
    elif "예산" in message or "돈" in message:
        response = "💰 예산을 고려한 맛집을 찾아드릴게요! 얼마 정도 생각하고 계신가요?"
        recommendations = ["1만원 이하 맛집", "2만원 이하 가성비", "3만원 이하 특별한날"]
    else:
        response = f"'{request.message}' 에 대해 검색 중이에요... 🔍 조금만 기다려주세요!"
        recommendations = ["추천 준비중"]
    
    return ChatResponse(
        response=response,
        user_id=request.user_id,
        timestamp=datetime.now().isoformat(),
        recommendations=recommendations
    )

if __name__ == "__main__":
    print("🚀 나비얌 챗봇 테스트 서버 시작!")
    print("📝 API 문서: http://localhost:8000/docs")
    print("🔍 대화 테스트: http://localhost:8000/chat")
    
    uvicorn.run(
        "test_simple_server:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )