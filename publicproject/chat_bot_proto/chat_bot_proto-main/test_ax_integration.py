#!/usr/bin/env python3
"""
A.X 3.1 Lite 통합 테스트
모델 팩토리를 통해 A.X 3.1 Lite가 정상 작동하는지 확인
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.config import get_default_config, get_config_summary
from models.model_factory import create_model, ModelFactory, ModelSelection

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_ax_model_creation():
    """A.X 3.1 Lite 모델 생성 테스트"""
    print("=== A.X 3.1 Lite 모델 생성 테스트 ===")
    
    try:
        # 기본 설정 가져오기
        config = get_default_config()
        print(get_config_summary(config))
        
        # A.X 3.1 Lite 모델 생성
        print("A.X 3.1 Lite 모델 생성 중...")
        ax_model = create_model(
            model_config=config.model,
            model_type="ax",
            cache_dir=config.data.cache_dir
        )
        
        print("A.X 3.1 Lite 모델 생성 성공!")
        
        # 모델 정보 확인
        model_info = ax_model.get_model_info()
        print("\n=== 모델 정보 ===")
        for key, value in model_info.items():
            print(f"{key}: {value}")
        
        # 간단한 생성 테스트
        print("\n=== 텍스트 생성 테스트 ===")
        test_prompts = [
            "10살 아이가 좋아할 치킨집 추천해주세요.",
            "가족이 함께 먹을 수 있는 맛있는 음식점 알려주세요."
        ]
        
        for prompt in test_prompts:
            print(f"\n프롬프트: {prompt}")
            result = ax_model.generate_text(prompt, max_new_tokens=50)
            
            if "error" in result:
                print(f"생성 실패: {result['error']}")
            else:
                print(f"생성 성공: {result['text']}")
                print(f"   - 생성 시간: {result['generation_time']:.2f}초")
                print(f"   - 토큰/초: {result['tokens_per_second']:.1f}")
        
        # 메모리 정리
        ax_model.cleanup_memory()
        print("\n메모리 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"A.X 3.1 Lite 모델 테스트 실패: {e}")
        return False

def test_model_factory():
    """모델 팩토리 기능 테스트"""
    print("\n=== 모델 팩토리 기능 테스트 ===")
    
    try:
        # 지원 모델 목록 확인
        supported_models = ModelFactory.list_supported_models()
        print("지원 모델:")
        for model_type, info in supported_models.items():
            print(f"  - {model_type}: {info['name']} - {info['description']}")
        
        # A.X 모델 정보 확인
        ax_info = ModelFactory.get_model_info("ax")
        print(f"\nA.X 모델 정보: {ax_info}")
        
        return True
        
    except Exception as e:
        print(f"모델 팩토리 테스트 실패: {e}")
        return False

def test_chatbot_integration():
    """챗봇 통합 테스트"""
    print("\n=== 챗봇 통합 테스트 ===")
    
    try:
        from inference.chatbot import NaviyamChatbot
        
        # 설정 가져오기
        config = get_default_config()
        config.model.model_type = "ax"  # A.X 3.1 Lite 명시적 설정
        
        # 챗봇 생성 (간단 버전)
        print("나비얌 챗봇 초기화 중...")
        chatbot = NaviyamChatbot(config)
        
        if chatbot.is_initialized:
            print("챗봇 초기화 성공!")
            
            # 간단한 대화 테스트
            test_message = "안녕하세요! 치킨 먹고 싶어요!"
            print(f"\n테스트 메시지: {test_message}")
            
            response = chatbot.chat(test_message, "test_user")
            print(f"챗봇 응답: {response}")
            
            # 성능 지표 확인
            metrics = chatbot.get_performance_metrics()
            print(f"\n응답 시간: {metrics.get('avg_response_time', 0):.2f}초")
            
            return True
        else:
            print("챗봇 초기화 실패")
            return False
            
    except Exception as e:
        print(f"챗봇 통합 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("A.X 3.1 Lite 통합 테스트 시작")
    
    setup_logging()
    
    tests = [
        ("모델 팩토리 기능", test_model_factory),
        ("A.X 3.1 Lite 모델 생성", test_ax_model_creation),
        ("챗봇 통합", test_chatbot_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"테스트: {test_name}")
        print(f"{'='*50}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"{test_name} 테스트 중 예외 발생: {e}")
            results[test_name] = False
    
    # 결과 요약
    print(f"\n{'='*50}")
    print("테스트 결과 요약")
    print(f"{'='*50}")
    
    for test_name, success in results.items():
        status = "성공" if success else "실패"
        print(f"{test_name}: {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n전체 결과: {success_count}/{total_count} 테스트 통과")
    
    if success_count == total_count:
        print("모든 테스트 통과! A.X 3.1 Lite 통합 완료!")
    else:
        print("일부 테스트 실패. 문제를 확인해주세요.")

if __name__ == "__main__":
    main()