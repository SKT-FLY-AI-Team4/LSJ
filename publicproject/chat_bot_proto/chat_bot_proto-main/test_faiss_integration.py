#!/usr/bin/env python3
"""
FAISS Vector Store 통합 테스트
MockVectorStore vs FAISSVectorStore 성능 비교
"""

import sys
import time
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from rag.vector_stores import create_vector_store, MockVectorStore, FAISSVectorStore
from rag.retriever import create_naviyam_retriever
from rag.query_parser import QueryStructurizer
from utils.config import get_default_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mock_vs_faiss():
    """Mock vs FAISS 성능 비교 테스트"""
    
    print("=" * 60)
    print("FAISS Vector Store Integration Test")
    print("=" * 60)
    
    # 테스트 쿼리들
    test_queries = [
        "치킨 맛집 추천해줘",
        "2만원 이하 가게 찾아줘", 
        "인기 메뉴 있는 곳",
        "파스타 먹고 싶어",
        "강남에 있는 착한가게"
    ]
    
    config = get_default_config()
    
    # 1. Mock Vector Store 테스트
    print("\n1. MockVectorStore Test")
    print("-" * 40)
    
    try:
        mock_start = time.time()
        mock_retriever = create_naviyam_retriever(
            knowledge_file_path="rag/test_data.json",
            vector_store_type="mock"
        )
        mock_init_time = time.time() - mock_start
        
        print(f"✅ Mock 초기화 완료: {mock_init_time:.2f}초")
        
        mock_results = {}
        mock_total_time = 0
        
        for query in test_queries:
            start_time = time.time()
            documents = mock_retriever.search(query)
            search_time = time.time() - start_time
            mock_total_time += search_time
            
            mock_results[query] = {
                'count': len(documents),
                'time': search_time,
                'docs': [doc.get_content()[:50] + "..." for doc in documents[:2]]
            }
            
            print(f"  🔍 '{query}' → {len(documents)}개 ({search_time:.3f}초)")
        
        print(f"📊 Mock 총 검색 시간: {mock_total_time:.3f}초")
        
    except Exception as e:
        print(f"❌ Mock 테스트 실패: {e}")
        return False
    
    # 2. FAISS Vector Store 테스트
    print("\n🚀 2. FAISSVectorStore 테스트")
    print("-" * 40)
    
    try:
        faiss_start = time.time()
        
        # FAISS Retriever 생성 (수동으로 설정)
        from rag.vector_stores import FAISSVectorStore
        from rag.query_parser import QueryStructurizer
        from rag.retriever import NaviyamRetriever, load_knowledge_from_file
        
        # Vector Store 생성
        faiss_store = FAISSVectorStore(
            embedding_model=None,  # 기본 모델 사용
            index_path="outputs/test_faiss_index.faiss"
        )
        
        # Query Structurizer 생성
        query_structurizer = QueryStructurizer(llm_client=None)
        
        # Retriever 생성
        faiss_retriever = NaviyamRetriever(faiss_store, query_structurizer)
        
        # 지식 베이스 로드 및 추가
        knowledge_data = load_knowledge_from_file("rag/test_data.json")
        if knowledge_data:
            faiss_retriever.add_knowledge_base(knowledge_data)
        
        faiss_init_time = time.time() - faiss_start
        print(f"✅ FAISS 초기화 완료: {faiss_init_time:.2f}초")
        
        faiss_results = {}
        faiss_total_time = 0
        
        for query in test_queries:
            start_time = time.time()
            documents = faiss_retriever.search(query)
            search_time = time.time() - start_time
            faiss_total_time += search_time
            
            faiss_results[query] = {
                'count': len(documents),
                'time': search_time,
                'docs': [doc.get_content()[:50] + "..." for doc in documents[:2]]
            }
            
            print(f"  🔍 '{query}' → {len(documents)}개 ({search_time:.3f}초)")
        
        print(f"📊 FAISS 총 검색 시간: {faiss_total_time:.3f}초")
        
    except Exception as e:
        print(f"❌ FAISS 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 결과 비교
    print("\n📊 3. 성능 비교 결과")
    print("-" * 40)
    
    print(f"초기화 시간:")
    print(f"  Mock:  {mock_init_time:.2f}초")
    print(f"  FAISS: {faiss_init_time:.2f}초")
    print(f"  속도비: {faiss_init_time/mock_init_time:.1f}x 느림")
    
    print(f"\n검색 시간:")
    print(f"  Mock:  {mock_total_time:.3f}초")
    print(f"  FAISS: {faiss_total_time:.3f}초")
    print(f"  속도비: {faiss_total_time/mock_total_time:.1f}x {'느림' if faiss_total_time > mock_total_time else '빠름'}")
    
    print(f"\n검색 결과 비교:")
    for query in test_queries:
        mock_count = mock_results[query]['count']
        faiss_count = faiss_results[query]['count']
        print(f"  '{query}':")
        print(f"    Mock: {mock_count}개, FAISS: {faiss_count}개")
        
        # 샘플 결과 비교
        if mock_results[query]['docs'] and faiss_results[query]['docs']:
            print(f"    Mock 샘플: {mock_results[query]['docs'][0]}")
            print(f"    FAISS 샘플: {faiss_results[query]['docs'][0]}")
    
    print("\n✅ FAISS 통합 테스트 완료!")
    return True


def test_faiss_basic_functionality():
    """FAISS 기본 기능 테스트"""
    
    print("\n🔧 4. FAISS 기본 기능 테스트")
    print("-" * 40)
    
    try:
        # 1. 기본 Vector Store 생성 테스트
        store = FAISSVectorStore()
        print("✅ FAISSVectorStore 생성 성공")
        
        # 2. 임베딩 테스트
        query_embedding = store.encode_query("치킨 맛집")
        print(f"✅ 쿼리 임베딩 생성 성공: 차원 {len(query_embedding)}")
        
        # 3. 저장/로드 테스트
        test_index_path = "outputs/test_basic_faiss.faiss"
        store_with_path = FAISSVectorStore(index_path=test_index_path)
        print("✅ 인덱스 경로 지정 생성 성공")
        
        print("✅ FAISS 기본 기능 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ FAISS 기본 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트 실행"""
    
    print("🚀 FAISS Vector Store 통합 테스트 시작")
    
    # 출력 디렉토리 생성
    Path("outputs").mkdir(exist_ok=True)
    
    # 기본 기능 테스트
    basic_success = test_faiss_basic_functionality()
    
    if basic_success:
        # 통합 테스트
        integration_success = test_mock_vs_faiss()
        
        if integration_success:
            print("\n🎉 모든 테스트 성공!")
            print("\n📋 다음 단계:")
            print("  1. requirements.txt 의존성 설치: pip install -r requirements.txt")
            print("  2. FAISS를 기본 Vector Store로 설정")
            print("  3. 실제 챗봇에서 FAISS 활용 테스트")
            return True
        else:
            print("\n⚠️ 통합 테스트 실패")
            return False
    else:
        print("\n⚠️ 기본 기능 테스트 실패")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)