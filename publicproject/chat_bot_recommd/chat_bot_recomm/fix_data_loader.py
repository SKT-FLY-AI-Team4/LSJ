#!/usr/bin/env python3
"""
데이터 로더 문제 해결
캐시 파일 삭제 및 RAG 시스템과 데이터 로더 동기화
"""

import os
import json
from pathlib import Path

def fix_data_loading_issues():
    """데이터 로딩 문제 해결"""
    
    print("=== 나비얌 챗봇 데이터 로더 문제 해결 ===")
    
    # 1. 손상된 캐시 파일 삭제
    cache_file = Path("cache/naviyam_knowledge.json")
    if cache_file.exists():
        print(f"손상된 캐시 파일 삭제: {cache_file}")
        cache_file.unlink()
        print("✅ 캐시 파일 삭제 완료")
    else:
        print("캐시 파일 없음")
    
    # 2. 캐시 디렉토리 정리
    cache_dir = Path("cache")
    if cache_dir.exists():
        for file in cache_dir.glob("*.json"):
            print(f"기존 캐시 파일 삭제: {file}")
            file.unlink()
    
    # 3. RAG 데이터 확인
    rag_data_file = Path("rag/test_data.json")
    if rag_data_file.exists():
        with open(rag_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ RAG 데이터 확인: {len(data.get('shops', {}))}개 가게, {len(data.get('menus', {}))}개 메뉴")
    else:
        print("❌ RAG 데이터 파일 없음!")
        return False
    
    # 4. 간단한 지식베이스 직접 생성 (캐시 대신)
    knowledge_cache = {
        "shops": data.get("shops", {}),
        "menus": data.get("menus", {}),
        "coupons": {},
        "reviews": [],
        "popular_combinations": []
    }
    
    # 5. 새로운 캐시 파일 생성
    cache_dir.mkdir(exist_ok=True)
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_cache, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 새로운 캐시 파일 생성 완료: {cache_file}")
    
    # 6. 빈 캐시 디렉토리 파일들 생성 (모델 캐시용)
    (cache_dir / ".gitkeep").touch()
    
    print("=== 수정 완료 ===")
    print("이제 'python main.py --mode chat --use_4bit' 실행해보세요!")
    
    return True

if __name__ == "__main__":
    success = fix_data_loading_issues()
    if success:
        print("\n✅ 모든 문제가 해결되었습니다!")
    else:
        print("\n❌ 문제 해결에 실패했습니다.")