#!/usr/bin/env python3
"""
FAISS 인덱스 사전 빌드 스크립트

이 스크립트는 test_data.json의 모든 데이터를 미리 임베딩하여 
FAISS 인덱스 파일과 메타데이터를 생성합니다.

챗봇 초기화 시 이 사전 생성된 파일들을 로드하여 
초기화 시간을 대폭 단축시킵니다.
"""

import time
import json
import logging
from pathlib import Path
import argparse
from typing import List, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_faiss_index(
    data_file: str = "rag/test_data.json",
    output_dir: str = "outputs",
    index_name: str = "prebuilt_faiss",
    embedding_model: str = "all-MiniLM-L6-v2"
):
    """
    FAISS 인덱스 사전 빌드
    
    Args:
        data_file: 소스 데이터 파일 경로
        output_dir: 출력 디렉토리
        index_name: 인덱스 파일명 (확장자 제외)
        embedding_model: 사용할 임베딩 모델명
    """
    logger.info("=== FAISS 인덱스 사전 빌드 시작 ===")
    start_time = time.time()
    
    try:
        # 1. 의존성 확인
        logger.info("의존성 라이브러리 확인...")
        import faiss
        from sentence_transformers import SentenceTransformer
        
        # 2. 데이터 로드
        logger.info(f"데이터 로드: {data_file}")
        if not Path(data_file).exists():
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_file}")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 3. Document 생성 및 텍스트 추출
        logger.info("Document 객체 생성...")
        from rag.documents import ShopDocument, MenuDocument
        
        documents = []
        texts = []
        
        # 가게 문서 생성
        shops_dict = {}
        shops_data = data.get('shops', {})
        for shop_id, shop_data in shops_data.items():
            doc = ShopDocument(shop_data)
            documents.append(doc)
            texts.append(doc.get_content())
            shops_dict[shop_data['id']] = shop_data
        
        # 메뉴 문서 생성  
        menus_data = data.get('menus', {})
        for menu_id, menu_data in menus_data.items():
            shop_info = shops_dict.get(menu_data.get('shop_id'), {})
            doc = MenuDocument(menu_data, shop_info)
            documents.append(doc)
            texts.append(doc.get_content())
        
        logger.info(f"총 {len(documents)}개 문서 준비 완료")
        
        # 4. 임베딩 모델 로드
        logger.info(f"임베딩 모델 로드: {embedding_model}")
        model_load_start = time.time()
        embedding_model_instance = SentenceTransformer(embedding_model)
        model_load_time = time.time() - model_load_start
        logger.info(f"모델 로드 완료: {model_load_time:.2f}초")
        
        # 5. 텍스트 임베딩 생성
        logger.info("텍스트 임베딩 생성...")
        embedding_start = time.time()
        embeddings = embedding_model_instance.encode(texts, convert_to_numpy=True)
        embedding_time = time.time() - embedding_start
        logger.info(f"임베딩 생성 완료: {embedding_time:.2f}초, 차원: {embeddings.shape}")
        
        # 6. FAISS 인덱스 생성
        logger.info("FAISS 인덱스 생성...")
        embedding_dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(embedding_dim)
        index.add(embeddings.astype('float32'))
        
        # 7. 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 8. FAISS 인덱스 파일 저장
        index_file_path = output_path / f"{index_name}.faiss"
        logger.info(f"FAISS 인덱스 저장: {index_file_path}")
        faiss.write_index(index, str(index_file_path))
        
        # 9. 메타데이터 준비
        logger.info("메타데이터 준비...")
        metadata_info = {
            "index_info": {
                "total_documents": len(documents),
                "embedding_dimension": embedding_dim,
                "embedding_model": embedding_model,
                "index_type": "IndexFlatL2",
                "created_at": time.time()
            },
            "document_mapping": {},  # {faiss_idx: doc_id}
            "documents_metadata": {},  # {doc_id: metadata}
            "documents_content": {}  # {doc_id: content} - 빠른 검색용
        }
        
        for i, doc in enumerate(documents):
            doc_id = doc.id
            faiss_idx = i
            
            metadata_info["document_mapping"][str(faiss_idx)] = doc_id
            metadata_info["documents_metadata"][doc_id] = doc.get_metadata()
            metadata_info["documents_content"][doc_id] = doc.get_content()
        
        # 10. 메타데이터 파일 저장
        metadata_file_path = output_path / f"{index_name}_metadata.json"
        logger.info(f"메타데이터 저장: {metadata_file_path}")
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_info, f, ensure_ascii=False, indent=2)
        
        # 11. 빌드 정보 저장
        build_info = {
            "build_time": time.time() - start_time,
            "model_load_time": model_load_time,
            "embedding_time": embedding_time,
            "total_documents": len(documents),
            "index_file": str(index_file_path),
            "metadata_file": str(metadata_file_path),
            "source_data": data_file,
            "embedding_model": embedding_model,
            "embedding_dimension": embedding_dim
        }
        
        build_info_path = output_path / f"{index_name}_build_info.json"
        with open(build_info_path, 'w', encoding='utf-8') as f:
            json.dump(build_info, f, ensure_ascii=False, indent=2)
        
        total_time = time.time() - start_time
        logger.info("=== FAISS 인덱스 빌드 완료 ===")
        logger.info(f"총 소요 시간: {total_time:.2f}초")
        logger.info(f"인덱스 파일: {index_file_path}")
        logger.info(f"메타데이터 파일: {metadata_file_path}")
        logger.info(f"빌드 정보: {build_info_path}")
        
        # 12. 검증 테스트
        logger.info("빌드된 인덱스 검증...")
        test_query = "치킨"
        test_embedding = embedding_model_instance.encode([test_query])
        distances, indices = index.search(test_embedding.astype('float32'), 3)
        
        logger.info(f"검증 쿼리 '{test_query}' 결과:")
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:
                doc_id = metadata_info["document_mapping"][str(idx)]
                content = metadata_info["documents_content"][doc_id][:100]
                logger.info(f"  {i+1}. [{distance:.4f}] {doc_id}: {content}...")
        
        return {
            "success": True,
            "build_time": total_time,
            "index_file": str(index_file_path),
            "metadata_file": str(metadata_file_path),
            "total_documents": len(documents)
        }
        
    except Exception as e:
        logger.error(f"FAISS 인덱스 빌드 실패: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="FAISS 인덱스 사전 빌드")
    parser.add_argument("--data", default="rag/test_data.json", help="소스 데이터 파일")
    parser.add_argument("--output", default="outputs", help="출력 디렉토리")
    parser.add_argument("--name", default="prebuilt_faiss", help="인덱스 파일명")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="임베딩 모델")
    
    args = parser.parse_args()
    
    result = build_faiss_index(
        data_file=args.data,
        output_dir=args.output,
        index_name=args.name,
        embedding_model=args.model
    )
    
    if result["success"]:
        print("SUCCESS: FAISS 인덱스 빌드 성공!")
        print(f"인덱스 파일: {result['index_file']}")
        print(f"총 문서 수: {result['total_documents']}")
        print(f"빌드 시간: {result['build_time']:.2f}초")
    else:
        print("ERROR: FAISS 인덱스 빌드 실패!")
        print(f"오류: {result['error']}")

if __name__ == "__main__":
    main()