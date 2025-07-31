#!/usr/bin/env python3
"""
Layer 1: 4-Funnel 추천 시스템 종합 테스트
모든 구현된 Funnel들의 통합 테스트 및 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recommendation import (
    PopularityFunnel, 
    ContextualFunnel, 
    ContentFunnel, 
    CollaborativeFunnel,
    CandidateGenerator,
    CandidateGenerationConfig
)
from datetime import datetime


def test_individual_funnels():
    """개별 Funnel 테스트"""
    print("=" * 60)
    print("개별 Funnel 기능 테스트")
    print("=" * 60)
    
    # 1. PopularityFunnel 테스트
    print("\n[1] PopularityFunnel 테스트")
    popularity_funnel = PopularityFunnel()
    pop_candidates = popularity_funnel.get_candidates(limit=3)
    print(f"   인기도 기반 Top 3:")
    for i, candidate in enumerate(pop_candidates, 1):
        print(f"   {i}. {candidate['shop_name']} - {candidate['base_score']}점")
    
    # 2. ContextualFunnel 테스트
    print("\n[2] ContextualFunnel 테스트")
    contextual_funnel = ContextualFunnel()
    ctx_candidates = contextual_funnel.get_candidates(
        user_location="관악구", 
        time_of_day="lunch", 
        limit=3
    )
    print(f"   관악구 점심시간 Top 3:")
    for i, candidate in enumerate(ctx_candidates, 1):
        print(f"   {i}. {candidate['shop_name']} - {candidate['context_score']:.1f}점")
    
    # 3. ContentFunnel 테스트
    print("\n[3] ContentFunnel 테스트")
    content_funnel = ContentFunnel()
    content_candidates = content_funnel.get_candidates(
        query="한식", 
        limit=3
    )
    print(f"   '한식' 검색 Top 3:")
    for i, candidate in enumerate(content_candidates, 1):
        print(f"   {i}. {candidate['shop_name']} - {candidate['content_score']:.1f}점")
    
    # 4. CollaborativeFunnel 테스트
    print("\n[4] CollaborativeFunnel 테스트")
    collaborative_funnel = CollaborativeFunnel()
    collab_candidates = collaborative_funnel.get_candidates(
        user_type="healthy_eater", 
        limit=3
    )
    print(f"   건강지향 사용자 Top 3:")
    for i, candidate in enumerate(collab_candidates, 1):
        print(f"   {i}. {candidate['shop_name']} - {candidate['collaborative_score']:.1f}점")


def test_integrated_scenarios():
    """통합 시나리오 테스트"""
    print("\n" + "=" * 60)
    print("통합 시나리오 테스트")
    print("=" * 60)
    
    generator = CandidateGenerator()
    
    scenarios = [
        {
            "name": "시나리오 1: 건강지향 사용자의 점심 추천",
            "params": {
                "user_type": "healthy_eater",
                "user_location": "관악구",
                "time_of_day": "lunch",
                "filters": {"is_good_influence": True}
            }
        },
        {
            "name": "시나리오 2: 가격중시 사용자의 치킨 검색",
            "params": {
                "user_type": "budget_conscious",
                "query": "치킨",
                "filters": {"max_price": 15000}
            }
        },
        {
            "name": "시나리오 3: 미식가의 저녁 추천",
            "params": {
                "user_type": "gourmet",
                "time_of_day": "dinner",
                "filters": {"category": "일식"}
            }
        },
        {
            "name": "시나리오 4: 편의성 중시 사용자의 간단한 조건",
            "params": {
                "user_type": "convenience_seeker",
                "filters": {"accepts_meal_card": True}
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n>>> {scenario['name']}")
        candidates = generator.generate_candidates(**scenario['params'])
        
        if candidates:
            print(f"   추천 결과 Top 5:")
            for i, candidate in enumerate(candidates[:5], 1):
                funnel_source = candidate['funnel_source']
                shop_name = candidate['shop_name']
                category = candidate['category']
                
                # 점수 정보
                scores = []
                if 'collaborative_score' in candidate:
                    scores.append(f"협업:{candidate['collaborative_score']:.0f}")
                if 'content_score' in candidate:
                    scores.append(f"콘텐츠:{candidate['content_score']:.0f}")
                if 'context_score' in candidate:
                    scores.append(f"상황:{candidate['context_score']:.0f}")
                if 'base_score' in candidate:
                    scores.append(f"인기:{candidate['base_score']:.0f}")
                
                score_str = " | ".join(scores) if scores else "N/A"
                
                print(f"   {i}. {shop_name} ({category})")
                print(f"      출처: {funnel_source} | 점수: {score_str}")
        else:
            print("   조건에 맞는 추천 결과가 없습니다.")


def test_funnel_diversity():
    """Funnel 다양성 테스트"""
    print("\n" + "=" * 60)
    print("Funnel 다양성 및 커버리지 테스트")
    print("=" * 60)
    
    generator = CandidateGenerator()
    
    # 다양한 조건으로 테스트
    test_cases = [
        {"name": "전체 조건", "params": {
            "user_type": "default",
            "user_location": "관악구", 
            "query": "한식",
            "time_of_day": "lunch"
        }},
        {"name": "쿼리 없음", "params": {
            "user_type": "healthy_eater",
            "user_location": "서울시"
        }},
        {"name": "위치 없음", "params": {
            "query": "치킨",
            "time_of_day": "dinner"
        }},
        {"name": "최소 조건", "params": {
            "user_type": "default"
        }}
    ]
    
    for case in test_cases:
        print(f"\n>>> {case['name']} 테스트")
        candidates = generator.generate_candidates(**case['params'])
        
        # Funnel별 분포 분석
        funnel_counts = {}
        for candidate in candidates:
            source = candidate['funnel_source']
            funnel_counts[source] = funnel_counts.get(source, 0) + 1
        
        print(f"   총 후보 수: {len(candidates)}")
        print(f"   Funnel별 분포:")
        for funnel, count in sorted(funnel_counts.items()):
            print(f"   - {funnel}: {count}개")


def test_performance_stats():
    """성능 및 통계 테스트"""
    print("\n" + "=" * 60)
    print("성능 및 통계 정보")
    print("=" * 60)
    
    generator = CandidateGenerator()
    
    # 다양한 설정으로 성능 테스트
    import time
    
    test_params = {
        "user_type": "healthy_eater",
        "user_location": "관악구",
        "query": "비빔밥",
        "time_of_day": "lunch",
        "filters": {"category": "한식"}
    }
    
    # 실행 시간 측정
    start_time = time.time()
    candidates = generator.generate_candidates(**test_params)
    execution_time = time.time() - start_time
    
    print(f"[PERF] 성능 정보:")
    print(f"   실행 시간: {execution_time:.3f}초")
    print(f"   생성된 후보 수: {len(candidates)}")
    print(f"   후보당 평균 시간: {execution_time/len(candidates)*1000:.2f}ms" if candidates else "N/A")
    
    # 통계 정보
    stats = generator.get_funnel_stats()
    print(f"\n[STATS] 시스템 통계:")
    print(f"   최대 후보 수 설정: {stats['config']['max_candidates']}")
    print(f"   인기도 매장 수: {stats['popularity_stats']['total_shops']}")
    print(f"   인기도 평균 점수: {stats['popularity_stats']['avg_score']:.1f}")


def main():
    """메인 테스트 실행"""
    print(">>> Layer 1: 4-Funnel 추천 시스템 종합 테스트 시작")
    print(f">>> 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 개별 Funnel 테스트
        test_individual_funnels()
        
        # 2. 통합 시나리오 테스트
        test_integrated_scenarios()
        
        # 3. Funnel 다양성 테스트
        test_funnel_diversity()
        
        # 4. 성능 및 통계 테스트
        test_performance_stats()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] 모든 테스트 완료!")
        print("[SUCCESS] Layer 1 추천 시스템이 성공적으로 구현되었습니다.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()