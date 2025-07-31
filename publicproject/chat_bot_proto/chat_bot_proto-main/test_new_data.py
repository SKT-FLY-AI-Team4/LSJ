#!/usr/bin/env python3
"""
새로운 실제 데이터로 챗봇 테스트
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from utils.config import parse_config
from inference.chatbot import create_naviyam_chatbot
import logging

# 로깅 레벨을 WARNING으로 설정하여 이모지 오류 회피
logging.basicConfig(level=logging.WARNING)

def test_chatbot():
    """챗봇 기능 테스트"""
    try:
        # 설정 로드
        config = parse_config()
        config.debug = False  # 디버그 모드 끄기
        
        print("챗봇 초기화 중...")
        chatbot = create_naviyam_chatbot(config)
        
        # 테스트 케이스들
        test_cases = [
            "치킨 먹고 싶어",
            "관악구 맛집 알려줘",
            "급식카드 쓸 수 있는 곳 있어?",
            "청년밥상문간이 뭐야?",
            "돈까스 맛집 추천해줘"
        ]
        
        print("=== 실제 데이터로 챗봇 테스트 ===")
        print()
        
        for i, question in enumerate(test_cases, 1):
            print(f"{i}. 질문: {question}")
            try:
                response = chatbot.chat(question, "test_user")
                print(f"   답변: {response}")
            except Exception as e:
                print(f"   오류: {e}")
            print()
        
        # 데이터베이스 통계
        print("=== 데이터베이스 현황 ===")
        metrics = chatbot.get_performance_metrics()
        print(f"지식베이스 가게 수: {metrics['knowledge_base_size']['shops']}")
        print(f"지식베이스 메뉴 수: {metrics['knowledge_base_size']['menus']}")
        
        return True
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_chatbot()
    if success:
        print("테스트 완료!")
    else:
        print("테스트 실패!")