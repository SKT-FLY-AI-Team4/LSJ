"""
Phase 3 성능 측정 테스트
현재 시스템의 정확한 병목 지점을 측정합니다.
"""

import time
import logging
from utils.config import get_default_config
from inference.chatbot import NaviyamChatbot

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_current_performance():
    """현재 성능 측정"""
    print("Phase 3 성능 측정 시작")
    print("=" * 60)
    
    # 설정 생성
    config = get_default_config()
    config.rag.vector_store_type = "prebuilt_faiss"  # 최적화된 버전 사용
    config.model.model_type = "ax"  # A.X 3.1 Lite 사용
    
    print(f"설정:")
    print(f"  모델: {config.model.model_type} ({config.model.model_name})")
    print(f"  Vector Store: {config.rag.vector_store_type}")
    print(f"  양자화: {'4bit' if config.model.use_4bit else '8bit' if config.model.use_8bit else 'None'}")
    print()
    
    # 챗봇 초기화 (여기서 측정이 일어남)
    start_time = time.time()
    
    try:
        chatbot = NaviyamChatbot(config)
        total_time = time.time() - start_time
        
        print(f"총 초기화 시간: {total_time:.3f}초")
        
        if total_time <= 3.0:
            print("3초 목표 달성!")
            remaining = 3.0 - total_time
            print(f"   여유시간: {remaining:.3f}초")
        else:
            excess = total_time - 3.0
            print("3초 목표 미달성")
            print(f"   초과시간: {excess:.3f}초")
            print(f"   추가 최적화 필요!")
        
        # 간단한 채팅 테스트
        print("\n기능 테스트:")
        test_response = chatbot.chat("치킨집 추천해줘", "test_user")
        print(f"응답: {test_response[:100]}...")
        
        return total_time, chatbot
        
    except Exception as e:
        print(f"초기화 실패: {e}")
        return None, None

if __name__ == "__main__":
    total_time, chatbot = test_current_performance()
    
    if total_time:
        print(f"\n결과 요약:")
        print(f"  현재 초기화 시간: {total_time:.3f}초")
        print(f"  3초 목표 달성 여부: {'달성' if total_time <= 3.0 else '미달성'}")
        
        if total_time > 3.0:
            print(f"\n다음 단계: 병렬화 구현으로 {total_time-3.0:.3f}초 단축 필요")