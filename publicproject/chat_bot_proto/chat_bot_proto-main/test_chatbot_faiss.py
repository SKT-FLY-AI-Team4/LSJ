#!/usr/bin/env python3
"""
챗봇에서 FAISS Vector Store 실제 테스트
"""

import sys
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from utils.config import get_default_config


def test_chatbot_with_faiss():
    """챗봇에서 FAISS 사용 테스트"""
    print("=== Chatbot FAISS Integration Test ===")
    
    try:
        # 설정 생성 및 FAISS 활성화
        config = get_default_config()
        config.rag.vector_store_type = "faiss"  # Mock에서 FAISS로 전환
        config.rag.index_path = "outputs/chatbot_faiss_test.faiss"
        
        print(f"[CONFIG] Vector Store: {config.rag.vector_store_type}")
        print(f"[CONFIG] Index Path: {config.rag.index_path}")
        
        # 챗봇 초기화 (시간 측정)
        from inference.chatbot import NaviyamChatbot
        
        print("\n[INIT] Creating chatbot...")
        start_time = time.time()
        
        chatbot = NaviyamChatbot(config)
        
        init_time = time.time() - start_time
        print(f"[OK] Chatbot initialized in {init_time:.2f}s")
        
        # RAG 시스템 확인
        if hasattr(chatbot, 'retriever') and chatbot.retriever:
            store_type = type(chatbot.retriever.vector_store).__name__
            print(f"[OK] RAG system ready with {store_type}")
        else:
            print(f"[WARNING] RAG system not available")
            return False
        
        # 테스트 질문들
        test_queries = [
            "치킨 맛집 추천해줘",
            "2만원 이하에서 먹을 수 있는 곳 있을까?",
            "파스타 맛집 알려줘"
        ]
        
        print(f"\n[TEST] Testing {len(test_queries)} queries...")
        
        total_time = 0
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Query {i}: {query} ---")
            
            start_time = time.time()
            response = chatbot.chat(query, user_id="test_faiss_user")
            query_time = time.time() - start_time
            total_time += query_time
            
            print(f"[RESPONSE] ({query_time:.3f}s) {response[:100]}...")
            
            # RAG 검색 로그 확인을 위해 retriever 직접 테스트
            if chatbot.retriever:
                documents = chatbot.retriever.search(query)
                print(f"[RAG] Found {len(documents)} relevant documents")
        
        avg_time = total_time / len(test_queries)
        print(f"\n[PERFORMANCE]")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average per query: {avg_time:.3f}s")
        
        print(f"\n[SUCCESS] Chatbot FAISS integration test completed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Chatbot FAISS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_vs_faiss_in_chatbot():
    """챗봇에서 Mock vs FAISS 비교"""
    print("\n=== Mock vs FAISS in Chatbot ===")
    
    test_query = "치킨 맛집 추천해줘"
    
    try:
        # 1. Mock 테스트
        print("\n[MOCK TEST]")
        config_mock = get_default_config() 
        config_mock.rag.vector_store_type = "mock"
        
        from inference.chatbot import NaviyamChatbot
        chatbot_mock = NaviyamChatbot(config_mock)
        
        start_time = time.time()
        response_mock = chatbot_mock.chat(test_query)
        mock_time = time.time() - start_time
        
        print(f"Mock response ({mock_time:.3f}s): {response_mock[:80]}...")
        
        # 2. FAISS 테스트  
        print("\n[FAISS TEST]")
        config_faiss = get_default_config()
        config_faiss.rag.vector_store_type = "faiss"
        
        chatbot_faiss = NaviyamChatbot(config_faiss)
        
        start_time = time.time()
        response_faiss = chatbot_faiss.chat(test_query)
        faiss_time = time.time() - start_time
        
        print(f"FAISS response ({faiss_time:.3f}s): {response_faiss[:80]}...")
        
        # 비교
        print(f"\n[COMPARISON]")
        print(f"  Mock:  {mock_time:.3f}s")
        print(f"  FAISS: {faiss_time:.3f}s")
        print(f"  Speed ratio: {faiss_time/mock_time:.1f}x")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트"""
    print("FAISS Chatbot Integration Test")
    print("=" * 50)
    
    # 출력 디렉토리 생성
    Path("outputs").mkdir(exist_ok=True)
    
    # 1. 기본 FAISS 챗봇 테스트
    faiss_success = test_chatbot_with_faiss()
    
    if faiss_success:
        # 2. Mock vs FAISS 비교
        comparison_success = test_mock_vs_faiss_in_chatbot()
        
        if comparison_success:
            print("\n*** ALL TESTS SUCCESSFUL! ***")
            print("\n## Phase 2 Vector DB Integration COMPLETED!")
            print("\nNext Phase: Sample Data Integration")
            print("  - Integrate sample_data.xlsx with FAISS")
            print("  - Scale up to full dataset")
            print("  - Performance optimization")
            return True
    
    print("\n*** SOME TESTS FAILED ***")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)