#!/usr/bin/env python3
"""
FAISS Vector Store 간단 테스트
"""

import sys
import time
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_imports():
    """기본 임포트 테스트"""
    print("=== Basic Import Test ===")
    
    try:
        from rag.vector_stores import FAISSVectorStore
        print("[OK] FAISSVectorStore import success")
        
        from rag.retriever import create_naviyam_retriever
        print("[OK] create_naviyam_retriever import success")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False


def test_faiss_creation():
    """FAISS 생성 테스트"""
    print("\n=== FAISS Creation Test ===")
    
    try:
        from rag.vector_stores import FAISSVectorStore
        
        # FAISS 생성 시도
        store = FAISSVectorStore()
        print("[OK] FAISSVectorStore created successfully")
        
        # 임베딩 테스트
        embedding = store.encode_query("test query")
        print(f"[OK] Query embedding created: dimension {len(embedding)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] FAISS creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_retriever():
    """Mock Retriever 테스트 (기존 시스템)"""
    print("\n=== Mock Retriever Test ===")
    
    try:
        from rag.retriever import create_naviyam_retriever
        
        # Mock 기반 Retriever 생성
        retriever = create_naviyam_retriever(
            knowledge_file_path="rag/test_data.json",
            vector_store_type="mock"
        )
        print("[OK] Mock retriever created")
        
        # 검색 테스트
        documents = retriever.search("치킨 맛집")
        print(f"[OK] Search completed: {len(documents)} documents found")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Mock retriever test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트"""
    print("FAISS Integration Simple Test")
    print("=" * 50)
    
    # 출력 디렉토리 생성
    Path("outputs").mkdir(exist_ok=True)
    
    # 1. 기본 임포트 테스트
    if not test_basic_imports():
        print("\n[FAIL] Basic imports failed")
        return False
    
    # 2. Mock 시스템 테스트 (기존 시스템 검증)
    if not test_mock_retriever():
        print("\n[FAIL] Mock retriever test failed")
        return False
    
    # 3. FAISS 생성 테스트
    if not test_faiss_creation():
        print("\n[FAIL] FAISS creation test failed") 
        print("\nNote: You may need to install dependencies:")
        print("pip install faiss-cpu sentence-transformers")
        return False
    
    print("\n[SUCCESS] All basic tests passed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install faiss-cpu sentence-transformers")
    print("2. Run full integration test")
    print("3. Switch to FAISS in production")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)