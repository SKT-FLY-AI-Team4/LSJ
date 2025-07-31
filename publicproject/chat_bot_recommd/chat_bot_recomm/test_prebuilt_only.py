#!/usr/bin/env python3
"""
PrebuiltFAISS 성능 테스트 (최적화 방식만)
"""

import time
import logging
from utils.config import get_default_config
from inference.chatbot import NaviyamChatbot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_prebuilt_faiss():
    """PrebuiltFAISS 방식 테스트"""
    print("=== PrebuiltFAISS 최적화 방식 테스트 ===")
    
    config = get_default_config()
    config.rag.vector_store_type = "prebuilt_faiss"
    config.rag.index_path = "outputs/prebuilt_faiss.faiss"
    
    print("초기화 시작...")
    start_time = time.time()
    chatbot = NaviyamChatbot(config)
    init_time = time.time() - start_time
    print(f"초기화 완료: {init_time:.2f}초")
    
    # 간단한 쿼리 테스트
    print("쿼리 테스트...")
    query_start = time.time()
    response = chatbot.chat("치킨 추천해줘", "test_user")
    query_time = time.time() - query_start
    print(f"쿼리 완료: {query_time:.3f}초")
    
    # 결과 표시
    print(f"\n결과:")
    print(f"  초기화 시간: {init_time:.2f}초")
    print(f"  쿼리 시간: {query_time:.3f}초")
    print(f"  목표 달성: {'YES' if init_time <= 3.0 else 'NO'}")
    print(f"  응답 샘플: {response[:100]}...")
    
    return init_time, query_time

if __name__ == "__main__":
    print("PrebuiltFAISS 성능 테스트")
    print("=" * 40)
    test_prebuilt_faiss()