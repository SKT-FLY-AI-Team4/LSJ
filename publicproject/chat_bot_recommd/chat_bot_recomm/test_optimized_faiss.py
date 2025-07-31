#!/usr/bin/env python3
"""
최적화된 FAISS 성능 테스트

사전 빌드된 FAISS 인덱스를 사용하여 초기화 시간을 측정하고
기존 방식과 비교합니다.
"""

import time
import logging
from utils.config import get_default_config
from inference.chatbot import NaviyamChatbot

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_original_faiss():
    """기존 FAISS 방식 테스트"""
    print("=== 기존 FAISS 방식 테스트 ===")
    
    config = get_default_config()
    config.rag.vector_store_type = "faiss"
    config.rag.index_path = "outputs/final_test.faiss"
    
    start_time = time.time()
    chatbot = NaviyamChatbot(config)
    init_time = time.time() - start_time
    
    # 간단한 쿼리 테스트
    query_start = time.time()
    response = chatbot.chat("치킨 추천해줘", "test_user_original")
    query_time = time.time() - query_start
    
    print(f"초기화 시간: {init_time:.2f}초")
    print(f"쿼리 시간: {query_time:.3f}초")
    print(f"응답: {response[:100]}...")
    
    return init_time, query_time

def test_optimized_faiss():
    """최적화된 PrebuiltFAISS 방식 테스트"""
    print("\n=== 최적화된 PrebuiltFAISS 방식 테스트 ===")
    
    config = get_default_config()
    config.rag.vector_store_type = "prebuilt_faiss"
    config.rag.index_path = "outputs/prebuilt_faiss.faiss"
    
    start_time = time.time()
    chatbot = NaviyamChatbot(config)
    init_time = time.time() - start_time
    
    # 간단한 쿼리 테스트
    query_start = time.time()
    response = chatbot.chat("치킨 추천해줘", "test_user_optimized")
    query_time = time.time() - query_start
    
    print(f"초기화 시간: {init_time:.2f}초")
    print(f"쿼리 시간: {query_time:.3f}초")
    print(f"응답: {response[:100]}...")
    
    return init_time, query_time

def main():
    """메인 테스트 함수"""
    print("FAISS 초기화 시간 최적화 성능 테스트")
    print("=" * 50)
    
    try:
        # 1. 기존 방식 테스트
        original_init, original_query = test_original_faiss()
        
        # 2. 최적화된 방식 테스트  
        optimized_init, optimized_query = test_optimized_faiss()
        
        # 3. 성능 비교
        print("\n" + "=" * 50)
        print("성능 비교 결과")
        print("=" * 50)
        
        init_improvement = ((original_init - optimized_init) / original_init) * 100
        query_improvement = ((original_query - optimized_query) / original_query) * 100 if original_query > 0 else 0
        
        print(f"초기화 시간:")
        print(f"  기존 방식:     {original_init:.2f}초")
        print(f"  최적화 방식:   {optimized_init:.2f}초")
        print(f"  개선 효과:     {init_improvement:.1f}% 단축")
        
        print(f"\n쿼리 시간:")
        print(f"  기존 방식:     {original_query:.3f}초")
        print(f"  최적화 방식:   {optimized_query:.3f}초")
        print(f"  개선 효과:     {query_improvement:.1f}% {'단축' if query_improvement > 0 else '증가'}")
        
        # 4. 목표 달성 여부 확인
        print(f"\n목표 달성 여부:")
        print(f"  목표: 3초 이하")
        print(f"  결과: {optimized_init:.2f}초")
        
        if optimized_init <= 3.0:
            print("  SUCCESS: 목표 달성! 3초 이하 달성")
        else:
            print("  FAILED: 목표 미달성, 추가 최적화 필요")
            
        # 5. 추가 분석
        print(f"\n추가 분석:")
        print(f"  시간 절약:     {original_init - optimized_init:.2f}초")
        print(f"  속도 배수:     {original_init / optimized_init:.1f}배 빨라짐")
        
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
        print(f"ERROR: 테스트 실패: {e}")

if __name__ == "__main__":
    main()