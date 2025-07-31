#!/usr/bin/env python3
"""
A.X 3.1 Lite 데모 스크립트
새로운 모델 팩토리를 통한 A.X 3.1 Lite 실행 데모
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.config import get_default_config
from models.model_factory import create_model

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    """A.X 3.1 Lite 데모"""
    print("A.X 3.1 Lite 나비얌 챗봇 데모")
    print("="*50)
    
    setup_logging()
    
    # 기본 설정 가져오기
    config = get_default_config()
    
    print("A.X 3.1 Lite 모델 로딩...")
    
    try:
        # A.X 3.1 Lite 모델 생성
        model = create_model(
            model_config=config.model,
            model_type="ax",
            cache_dir=config.data.cache_dir
        )
        
        print("모델 로딩 완료!")
        
        # 모델 정보 출력
        model_info = model.get_model_info()
        print(f"모델: {model_info['model_name']}")
        print(f"디바이스: {model_info['device']}")
        print(f"양자화: {model_info['quantization']}")
        
        # 나비얌 특화 테스트 프롬프트
        test_prompts = [
            "10살 아이가 좋아할 맛있는 음식점 추천해주세요.",
            "가족이 함께 가서 2만원으로 먹을 수 있는 곳 알려주세요.",
            "매운 걸 못 먹는 아이를 위한 순한 음식 추천해주세요.",
            "친구들과 함께 갈 수 있는 재미있는 카페 알려주세요."
        ]
        
        print("\n나비얌 특화 응답 테스트:")
        print("="*50)
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n{i}. 질문: {prompt}")
            
            # 텍스트 생성
            result = model.generate_text(
                prompt, 
                max_new_tokens=80,
                temperature=0.7
            )
            
            if "error" in result:
                print(f"   응답 실패: {result['error']}")
            else:
                print(f"   응답: {result['text']}")
                print(f"   생성시간: {result['generation_time']:.2f}초")
                print(f"   속도: {result['tokens_per_second']:.1f} 토큰/초")
        
        # 성능 벤치마크
        print(f"\n{'='*50}")
        print("성능 벤치마크 테스트")
        print(f"{'='*50}")
        
        benchmark_results = model.benchmark_generation(test_prompts[:2], num_runs=2)
        
        print(f"전체 평균 속도: {benchmark_results['overall_avg_tps']:.1f} 토큰/초")
        
        for result in benchmark_results['benchmark_results']:
            print(f"프롬프트: {result['prompt']}")
            print(f"  평균 생성시간: {result['avg_generation_time']:.2f}초")
            print(f"  평균 속도: {result['avg_tokens_per_second']:.1f} 토큰/초")
        
        # 메모리 정리
        model.cleanup_memory()
        print("\n메모리 정리 완료")
        
        print(f"\n{'='*50}")
        print("A.X 3.1 Lite 통합 성공!")
        print("나비얌 챗봇에서 A.X 3.1 Lite 모델이 정상 작동합니다.")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()