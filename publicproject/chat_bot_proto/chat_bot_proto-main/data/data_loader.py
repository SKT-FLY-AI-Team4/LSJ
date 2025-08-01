"""
나비얌 데이터 로더 (간단화 버전)
RAG 시스템과 동일한 test_data.json 사용
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from data.data_structure import (
    NaviyamShop, NaviyamMenu, NaviyamCoupon,
    NaviyamKnowledge, TrainingData, IntentType, ExtractedEntity
)

logger = logging.getLogger(__name__)


class NaviyamDataLoader:
    """나비얌 데이터 로더 (RAG 동기화 버전)"""

    def __init__(self, data_config, debug: bool = False):
        """
        Args:
            data_config: DataConfig 객체
            debug: 디버그 모드 여부
        """
        self.data_path = Path(data_config.data_path)
        self.output_path = Path(data_config.output_path)
        self.cache_dir = Path(data_config.cache_dir)
        self.max_conversations = data_config.max_conversations
        self.save_processed = data_config.save_processed
        self.debug = debug

        self.knowledge = NaviyamKnowledge()

        # 디렉토리 생성
        self.output_path.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

        # RAG 데이터 파일 경로
        self.rag_data_file = Path("rag/test_data.json")

    def load_all_data(self) -> NaviyamKnowledge:
        """RAG 시스템과 동일한 데이터 로드"""
        try:
            logger.info("나비얌 데이터 로딩 시작 (RAG 동기화)...")
            
            # RAG 데이터 파일에서 직접 로드
            if not self.rag_data_file.exists():
                logger.error(f"RAG 데이터 파일 없음: {self.rag_data_file}")
                raise FileNotFoundError(f"RAG 데이터 파일이 없습니다: {self.rag_data_file}")
            
            with open(self.rag_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"RAG 데이터 로드: {len(data.get('shops', {}))}개 가게, {len(data.get('menus', {}))}개 메뉴")
            
            # shops 로드
            for shop_id, shop_data in data.get('shops', {}).items():
                shop = NaviyamShop(
                    id=int(shop_data['id']),
                    name=shop_data['name'],
                    category=shop_data['category'],
                    is_good_influence_shop=shop_data.get('is_good_influence_shop', False),
                    is_food_card_shop=shop_data.get('is_food_card_shop', 'N'),
                    address=shop_data.get('address', ''),
                    open_hour=shop_data.get('open_hour', ''),
                    close_hour=shop_data.get('close_hour', ''),
                    owner_message=shop_data.get('owner_message'),
                    ordinary_discount=shop_data.get('ordinary_discount', False)
                )
                self.knowledge.shops[shop.id] = shop
            
            # menus 로드
            for menu_id, menu_data in data.get('menus', {}).items():
                menu = NaviyamMenu(
                    id=int(menu_data['id']),
                    shop_id=int(menu_data['shop_id']),
                    name=menu_data['name'],
                    price=int(menu_data.get('price', 0)),
                    description=menu_data.get('description', ''),
                    category=menu_data.get('category', '기타'),
                    is_popular=menu_data.get('is_popular', False)
                )
                self.knowledge.menus[menu.id] = menu
            
            # 기타 데이터
            self.knowledge.reviews = data.get('reviews', [])
            self.knowledge.popular_combinations = data.get('popular_combinations', [])
            
            # 쿠폰은 빈 딕셔너리로 초기화
            self.knowledge.coupons = {}

            logger.info(f"지식베이스 로드 완료: 가게 {len(self.knowledge.shops)}개, 메뉴 {len(self.knowledge.menus)}개")
            return self.knowledge

        except Exception as e:
            logger.error(f"데이터 로딩 실패: {e}")
            raise

    def get_training_conversations(self) -> List[TrainingData]:
        """학습용 대화 데이터 생성"""
        training_data = []
        max_items = self.max_conversations if not self.debug else 10

        # 인기 메뉴 기반 대화 생성
        popular_menus = [menu for menu in self.knowledge.menus.values() if menu.is_popular]
        menu_count = 0
        for menu in popular_menus:
            if menu_count >= max_items:
                break
            training_item = TrainingData(
                input_text=f"{menu.name} 추천해줘",
                target_intent=IntentType.FOOD_REQUEST,
                target_entities=ExtractedEntity(food_type=menu.name),
                expected_response=f"{menu.name}는 인기 메뉴예요! {menu.price}원에 드실 수 있어요"
            )
            training_data.append(training_item)
            menu_count += 1

        logger.info(f"학습용 대화 데이터 생성: {len(training_data)}개")
        return training_data


# 편의 함수들
def load_naviyam_data(data_config, debug: bool = False) -> NaviyamKnowledge:
    """나비얌 데이터 로드 (간편 함수)"""
    loader = NaviyamDataLoader(data_config, debug)
    return loader.load_all_data()


def generate_training_data(data_config, debug: bool = False) -> List[TrainingData]:
    """학습 데이터 생성 (간편 함수)"""
    loader = NaviyamDataLoader(data_config, debug)
    loader.load_all_data()
    return loader.get_training_conversations()
