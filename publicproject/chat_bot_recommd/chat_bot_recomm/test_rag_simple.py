"""
Simple RAG Integration Test
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data.data_structure import UserInput, IntentType
from inference.chatbot import NaviyamChatbot
from utils.config import AppConfig

def main():
    print("=== RAG Integration Test ===")
    
    try:
        # 챗봇 초기화
        print("1. Initializing chatbot...")
        config = AppConfig()
        chatbot = NaviyamChatbot(config)
        print("   [OK] Chatbot initialized")
        
        # RAG 시스템 확인
        if hasattr(chatbot, 'retriever') and chatbot.retriever:
            print("   [OK] RAG system loaded")
        else:
            print("   [WARNING] RAG system not loaded")
        
        print()
        
        # 테스트 케이스
        test_query = "치킨 맛집 추천해줘"
        print(f"2. Testing query: '{test_query}'")
        
        from datetime import datetime
        
        user_input = UserInput(
            text=test_query,
            user_id="test_user",
            timestamp=datetime.now()
        )
        
        # 응답 생성
        response = chatbot.process_user_input(user_input)
        
        # 안전한 응답 출력 (이모지 제거)
        safe_text = response.response.text.encode('ascii', 'ignore').decode('ascii')
        print(f"   Response: {safe_text[:80]}...")
        print(f"   Intent: {response.extracted_info.intent.value}")
        print(f"   Recommendations: {len(response.response.recommendations)}")
        
        if response.response.recommendations:
            print("   First recommendation:")
            first_rec = response.response.recommendations[0]
            name = first_rec.get('name', 'Unknown')
            category = first_rec.get('category', first_rec.get('type', 'Unknown'))
            print(f"     - {name} ({category})")
        
        print("\n[SUCCESS] RAG integration test completed!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)