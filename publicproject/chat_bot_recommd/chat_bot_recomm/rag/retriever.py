"""
RAG 시스템의 핵심 Retriever

QueryStructurizer, VectorStore, Documents를 통합하여
사용자 질문에 대한 관련 문서를 검색하는 메인 컴포넌트
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .documents import Document, ShopDocument, MenuDocument
from .vector_stores import VectorStore, create_vector_store
from .query_parser import QueryStructurizer, StructuredQuery

logger = logging.getLogger(__name__)


class NaviyamRetriever:
    """나비얌 RAG 시스템의 메인 Retriever 클래스"""
    
    def __init__(self, 
                 vector_store: VectorStore,
                 query_structurizer: QueryStructurizer,
                 top_k: int = 5):
        """
        Args:
            vector_store: Vector DB 구현체
            query_structurizer: 쿼리 구조화기
            top_k: 검색할 문서 수
        """
        self.vector_store = vector_store
        self.query_structurizer = query_structurizer
        self.top_k = top_k
        logger.info(f"NaviyamRetriever initialized (top_k={top_k})")
    
    def add_knowledge_base(self, knowledge_data: Dict[str, Any]):
        """지식 베이스 데이터를 Vector Store에 추가
        
        Args:
            knowledge_data: naviyam_knowledge.json 형태의 데이터
        """
        documents = []
        
        # 가게 정보 처리
        shops_data = knowledge_data.get('shops', {})
        menus_data = knowledge_data.get('menus', {})
        
        # ShopDocument 생성
        for shop_id, shop_info in shops_data.items():
            doc = ShopDocument(shop_info)
            documents.append(doc)
        
        # MenuDocument 생성 (가게 정보와 함께)
        for menu_id, menu_info in menus_data.items():
            shop_id = str(menu_info.get('shop_id'))
            shop_info = shops_data.get(shop_id, {})
            doc = MenuDocument(menu_info, shop_info)
            documents.append(doc)
        
        # Vector Store에 추가
        self.vector_store.add_documents(documents)
        logger.info(f"지식 베이스 추가 완료: {len(documents)}개 문서")
    
    def search(self, user_query: str) -> List[Document]:
        """사용자 질문에 대한 관련 문서 검색
        
        Args:
            user_query: 사용자의 자연어 질문
            
        Returns:
            관련도 높은 Document 리스트
        """
        # 1. 자연어 질문을 구조화된 쿼리로 변환
        structured_query = self.query_structurizer.parse_query(user_query)
        logger.info(f"구조화된 쿼리: {structured_query.semantic_query}")
        logger.info(f"필터: {structured_query.filters.model_dump(exclude_none=True)}")
        
        # 2. Vector Store에서 검색
        # 실제 임베딩 생성 (FAISS용) 또는 더미 벡터 (Mock용)
        if hasattr(self.vector_store, 'encode_query'):
            # FAISS 등 실제 Vector DB인 경우
            query_embedding = self.vector_store.encode_query(structured_query.semantic_query)
        else:
            # Mock Vector Store인 경우
            query_embedding = [0.1] * 384  # 임시 embedding
        
        filters = structured_query.filters.model_dump(exclude_none=True)
        doc_ids = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
            filters=filters
        )
        
        # 3. Document 객체들 반환
        documents = self.vector_store.get_documents_by_ids(doc_ids)
        logger.info(f"검색 완료: {len(documents)}개 문서 반환")
        
        return documents
    
    def get_context_for_llm(self, user_query: str) -> str:
        """LLM에게 전달할 컨텍스트 생성
        
        Args:
            user_query: 사용자 질문
            
        Returns:
            LLM용 컨텍스트 문자열
        """
        documents = self.search(user_query)
        
        if not documents:
            return "관련된 가게나 메뉴 정보를 찾을 수 없습니다."
        
        context_parts = ["다음은 관련된 가게 및 메뉴 정보입니다:"]
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"\n{i}. {doc.get_content()}")
        
        return "\n".join(context_parts)


def load_knowledge_from_file(file_path: str) -> Dict[str, Any]:
    """파일에서 지식 베이스 로드
    
    Args:
        file_path: naviyam_knowledge.json 파일 경로
        
    Returns:
        지식 베이스 데이터
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"지식 베이스 로드 실패: {e}")
        return {}


def create_naviyam_retriever(knowledge_file_path: str,
                           vector_store_type: str = "mock",
                           llm_client=None) -> NaviyamRetriever:
    """NaviyamRetriever 팩토리 함수
    
    Args:
        knowledge_file_path: 지식 베이스 파일 경로
        vector_store_type: Vector Store 타입 ("mock", "faiss", etc.)
        llm_client: LLM 클라이언트 (선택사항)
        
    Returns:
        설정된 NaviyamRetriever 인스턴스
    """
    # Vector Store 생성
    if vector_store_type == "prebuilt_faiss":
        vector_store = create_vector_store(
            store_type=vector_store_type,
            index_path="outputs/prebuilt_faiss.faiss",
            metadata_path="outputs/prebuilt_faiss_metadata.json"
        )
    else:
        vector_store = create_vector_store(
            store_type=vector_store_type,
            storage_path="outputs/rag_debug.json"  # Mock용 디버그 파일
        )
    
    # Query Structurizer 생성
    query_structurizer = QueryStructurizer(llm_client)
    
    # Retriever 생성
    retriever = NaviyamRetriever(vector_store, query_structurizer)
    
    # 지식 베이스 로드 및 추가 (PrebuiltFAISS는 이미 로드됨)
    if vector_store_type != "prebuilt_faiss":
        knowledge_data = load_knowledge_from_file(knowledge_file_path)
        if knowledge_data:
            retriever.add_knowledge_base(knowledge_data)
    else:
        logger.info("PrebuiltFAISS 사용: 지식 베이스 이미 로드됨")
    
    return retriever


# 테스트용 함수
def test_retriever():
    """Retriever 테스트"""
    knowledge_file = "rag/test_data.json"
    
    # Retriever 생성
    retriever = create_naviyam_retriever(knowledge_file, "mock")
    
    # 테스트 질문들
    test_queries = [
        "치킨 맛집 추천해줘",
        "2만원 이하 가게 찾아줘",
        "강남에 있는 착한가게",
        "인기 메뉴 있는 곳"
    ]
    
    for query in test_queries:
        print(f"\n=== 질문: {query} ===")
        
        # 검색 결과
        documents = retriever.search(query)
        print(f"검색된 문서 수: {len(documents)}")
        
        for i, doc in enumerate(documents, 1):
            print(f"{i}. [{doc.get_metadata()['type']}] {doc.get_content()[:100]}...")
        
        # LLM용 컨텍스트
        context = retriever.get_context_for_llm(query)
        print(f"\nLLM 컨텍스트 길이: {len(context)} 문자")


if __name__ == "__main__":
    test_retriever()