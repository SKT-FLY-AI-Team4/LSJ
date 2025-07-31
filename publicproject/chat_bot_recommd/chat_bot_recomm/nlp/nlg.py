"""
자연어 생성 (NLG) 모듈
구조화된 정보를 자연스러운 응답으로 변환
"""

import random
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, time
from enum import Enum

from data.data_structure import (
    IntentType, NaviyamShop, NaviyamMenu, NaviyamCoupon,
    UserProfile, ChatbotResponse
)
from .preprocessor import EmotionType
from utils.emoji_manager import enhance_response, EmojiContext, naviyam_emoji_manager

logger = logging.getLogger(__name__)


class ResponseTone(Enum):
    """응답 톤"""
    FRIENDLY = "friendly"  # 친근한
    EXCITED = "excited"  # 신나는
    PROFESSIONAL = "professional"  # 전문적
    CASUAL = "casual"  # 캐주얼
    ENCOURAGING = "encouraging"  # 격려하는
    EMPATHETIC = "empathetic"


class ResponseTemplate:
    """응답 템플릿"""

    def __init__(self, templates: List[str], tone: ResponseTone, variables: List[str] = None):
        self.templates = templates
        self.tone = tone
        self.variables = variables or []


class NaviyamNLG:
    """나비얌 자연어 생성 엔진"""

    def __init__(self, default_tone: ResponseTone = ResponseTone.FRIENDLY):
        """
        Args:
            default_tone: 기본 응답 톤
        """
        self.default_tone = default_tone

        # 응답 템플릿들 구축
        self.response_templates = self._build_response_templates()

        # 아동 친화적 표현들
        self.child_friendly_expressions = {
            'positive': ['좋아요!', '맛있겠어요!', '훌륭해요!', '완전 좋은데요?', '대박이에요!'],
            'encouragement': ['한번 가보세요!', '추천드려요!', '어떠세요?', '가보시는 거 어때요?'],
            'excitement': ['와!', '우와!', '대박!', '쩐다!', '진짜 좋아요!'],
            'empathy': ['그렇죠!', '맞아요!', '이해해요!', '공감해요!'],
            'transition': ['그런데', '참고로', '아, 그리고', '혹시나 해서 말씀드리면']
        }

        # 이모지 매니저 사용 (통합 관리)
        self.emoji_manager = naviyam_emoji_manager

    def _build_response_templates(self) -> Dict[IntentType, Dict[str, ResponseTemplate]]:
        """응답 템플릿 구축"""
        templates = {}

        # 음식 추천 요청 응답
        templates[IntentType.FOOD_REQUEST] = {
            'with_recommendations': ResponseTemplate([
                "{food_type} 좋은 선택이에요! {shop_name}에서 {menu_name}({price}원) 어떠세요?",
                "{shop_name}의 {menu_name} 추천드려요! {price}원이고 정말 맛있어요!",
                "오! {food_type} 드시고 싶으시군요. {shop_name} 가보세요! {menu_name}가 {price}원에 있어요.",
                "{food_type}라면 {shop_name}이 짱이에요! {menu_name} {price}원에 드실 수 있어요!"
            ], ResponseTone.FRIENDLY, ['food_type', 'shop_name', 'menu_name', 'price']),

            'good_influence_shop': ResponseTemplate([
                "착한가게 {shop_name} 추천드려요! {menu_name}({price}원)도 맛있고 의미도 있어요!",
                "{shop_name}는 착한가게예요! {menu_name} 드시면서 좋은 일도 하게 되는 거죠 ✨",
                "좋은 곳 알려드릴게요! {shop_name}은 착한가게이면서 {menu_name}도 {price}원에 맛있어요!"
            ], ResponseTone.ENCOURAGING, ['shop_name', 'menu_name', 'price']),

            'no_specific_food': ResponseTemplate([
                "음식 추천해드릴게요! 어떤 종류 드시고 싶으세요? 한식, 중식, 일식 중에 골라보세요!",
                "맛있는 거 많아요! 예산이나 선호하는 음식 종류 알려주시면 더 정확히 추천드릴게요!",
                "뭐 드실지 고민되시죠? 평소 좋아하시는 음식이나 오늘 기분을 알려주세요!"
            ], ResponseTone.FRIENDLY)
        }

        # 예산 관련 응답
        templates[IntentType.BUDGET_INQUIRY] = {
            'within_budget': ResponseTemplate([
                "{budget}원이면 {menu_list} 드실 수 있어요!",
                "{budget}원 예산으로 {menu_count}개 메뉴 중에 고르실 수 있어요! {menu_list} 어떠세요?",
                "완전 가능해요! {budget}원으로 {menu_list} 다 드실 수 있어요!"
            ], ResponseTone.FRIENDLY, ['budget', 'menu_list', 'menu_count']),

            'over_budget': ResponseTemplate([
                "음.. {budget}원은 좀 부족할 것 같아요. {alternative_budget}원 정도면 {menu_list} 드실 수 있어요!",
                "{budget}원으로는 조금 어려워요 ㅠㅠ 하지만 {alternative_budget}원만 더 있으면 {menu_list} 가능해요!",
                "예산을 조금만 더 올려주시면 좋을 것 같아요! {alternative_budget}원 정도로 {menu_list} 어떠세요?"
            ], ResponseTone.EMPATHETIC, ['budget', 'alternative_budget', 'menu_list']),

            'budget_tips': ResponseTemplate([
                "가성비 좋은 곳 알려드릴게요! {shop_name}에서 {menu_name} {price}원에 푸짐하게 드실 수 있어요!",
                "혜자 메뉴 발견! {shop_name}의 {menu_name}는 {price}원인데 양도 많고 맛도 좋아요!",
                "돈 아끼는 팁! {shop_name}에서 {discount_info} 있어서 더 저렴하게 드실 수 있어요!"
            ], ResponseTone.EXCITED, ['shop_name', 'menu_name', 'price', 'discount_info'])
        }

        # 위치 관련 응답
        templates[IntentType.LOCATION_INQUIRY] = {
            'nearby_shops': ResponseTemplate([
                "근처에 {shop_name} 있어요! 걸어서 {distance}분 거리예요.",
                "{location} 주변이면 {shop_name} 추천드려요! {walking_time}면 도착해요.",
                "가까운 곳으로는 {shop_name}이 있네요! {address}에 있어요."
            ], ResponseTone.FRIENDLY, ['shop_name', 'distance', 'location', 'walking_time', 'address']),

            'no_nearby': ResponseTemplate([
                "음.. 바로 근처에는 없네요 ㅠㅠ 조금만 더 가시면 {shop_name} 있어요!",
                "가까운 곳은 없지만 {transport_method}로 {time}분이면 {shop_name} 갈 수 있어요!",
                "근처에는 없어서 아쉽지만, {alternative_location}쪽에 좋은 곳들 많아요!"
            ], ResponseTone.EMPATHETIC, ['shop_name', 'transport_method', 'time', 'alternative_location'])
        }

        # 시간/운영시간 응답
        templates[IntentType.TIME_INQUIRY] = {
            'currently_open': ResponseTemplate([
                "{shop_name}는 지금 열려있어요! {close_time}까지 영업해요.",
                "다행히 아직 열려있어요! {shop_name} {close_time}까지 가능해요.",
                "좋은 타이밍이에요! {shop_name} 지금 바로 가시면 돼요. {close_time}까지 해요!"
            ], ResponseTone.FRIENDLY, ['shop_name', 'close_time']),

            'currently_closed': ResponseTemplate([
                "아 아쉽게도 {shop_name}는 지금 문 닫았어요 ㅠㅠ {open_time}에 다시 열어요!",
                "지금은 영업시간이 아니에요. {shop_name}는 {open_time}부터 {close_time}까지 해요.",
                "문 닫은 시간이네요... {open_time}에 다시 열으니까 그때 가보세요!"
            ], ResponseTone.EMPATHETIC, ['shop_name', 'open_time', 'close_time']),

            'break_time': ResponseTemplate([
                "{shop_name}는 지금 브레이크타임이에요! {break_end_time}에 다시 열어요.",
                "잠깐 쉬는 시간이네요. {break_end_time}까지 기다리시거나 다른 곳 어떠세요?",
                "아 브레이크타임이에요 ㅠㅠ {break_end_time}에 다시 문 열어요!"
            ], ResponseTone.EMPATHETIC, ['shop_name', 'break_end_time'])
        }

        # 쿠폰/할인 응답
        templates[IntentType.COUPON_INQUIRY] = {
            'available_coupons': ResponseTemplate([
                "쿠폰 있어요! {coupon_name}로 {discount_amount}원 할인받으실 수 있어요!",
                "대박! {coupon_name} 쿠폰으로 {discount_amount}원 아낄 수 있어요!",
                "혜택 발견! {coupon_name} 사용하시면 {discount_amount}원 할인이에요!"
            ], ResponseTone.EXCITED, ['coupon_name', 'discount_amount']),

            'coupon_conditions': ResponseTemplate([
                "{coupon_name} 쿠폰은 {min_amount}원 이상 주문하시면 사용 가능해요!",
                "조건이 있어요! {min_amount}원 이상 시키시면 {discount_amount}원 할인받으세요!",
                "{coupon_name}는 {min_amount}원 이상일 때 {discount_amount}원 깎아줘요!"
            ], ResponseTone.FRIENDLY, ['coupon_name', 'min_amount', 'discount_amount'])
        }

        # 일반 대화 응답
        templates[IntentType.GENERAL_CHAT] = {
            'greeting': ResponseTemplate([
                "안녕하세요! 맛있는 음식 찾아드릴게요! 😊",
                "안녕! 오늘 뭐 드시고 싶으세요?",
                "반가워요! 맛집 추천 도와드릴게요!"
            ], ResponseTone.FRIENDLY),

            'thanks': ResponseTemplate([
                "천만에요! 맛있게 드세요! 😊",
                "도움이 되었다니 기뻐요! 좋은 시간 보내세요!",
                "별말씀을요! 또 궁금한 거 있으면 언제든 물어보세요!"
            ], ResponseTone.FRIENDLY),

            'positive_feedback': ResponseTemplate([
                "와! 맛있으셨다니 정말 기뻐요! 🎉",
                "다행이에요! 또 맛있는 곳 찾아드릴게요!",
                "좋은 경험이셨군요! 다음에도 추천 받으러 오세요!"
            ], ResponseTone.EXCITED),

            'onboarding_questions': ResponseTemplate([
                "처음 오셨네요! 어떤 음식 찾고 계세요?",
                "반가워요! 뭐 드시고 싶은지 알려주세요!",
                "안녕하세요! 맛있는 음식 찾아드릴게요. 어떤 걸 원하세요?"
            ], ResponseTone.FRIENDLY),

            'data_collection': ResponseTemplate([
                "좀 더 알려주시면 더 잘 추천해드릴 수 있어요! {question}",
                "추천의 정확도를 높이려면 {question} 알려주세요!",
                "더 맞춤 추천을 위해 {question} 궁금해요!"
            ], ResponseTone.FRIENDLY, ['question']),

            'preference_questions': ResponseTemplate([
                "평소 {food_type} 중에서도 어떤 맛 좋아하세요?",
                "혹시 {preference_type} 선호하시는 편인가요?",
                "{food_type} 드실 때 중요하게 생각하는 게 있나요?"
            ], ResponseTone.FRIENDLY, ['food_type', 'preference_type'])
        }

        return templates

    def generate_response(
            self,
            intent: IntentType,
            entities: Dict[str, Any],
            recommendations: List[Dict] = None,
            user_profile: UserProfile = None,
            context: Dict[str, Any] = None
    ) -> ChatbotResponse:
        """응답 생성"""

        # 응답 톤 결정
        response_tone = self._determine_response_tone(intent, entities, user_profile)

        # 메인 응답 생성
        main_response = self._generate_main_response(
            intent, entities, recommendations, response_tone
        )

        # 추가 정보 생성
        additional_info = self._generate_additional_info(
            intent, entities, recommendations, user_profile
        )

        # 후속 질문 생성
        follow_up_questions = self._generate_follow_up_questions(
            intent, entities, recommendations
        )

        # 최종 응답 조합
        final_response = self._combine_response_parts(
            main_response, additional_info, response_tone
        )

        return ChatbotResponse(
            text=final_response,
            recommendations=recommendations or [],
            follow_up_questions=follow_up_questions,
            action_required=self._needs_action(intent),
            metadata={
                "intent": intent.value,
                "response_tone": response_tone.value,
                "generation_timestamp": datetime.now().isoformat()
            }
        )

    def _determine_response_tone(
            self,
            intent: IntentType,
            entities: Dict[str, Any],
            user_profile: UserProfile = None
    ) -> ResponseTone:
        """응답 톤 결정"""

        # 사용자 프로필 기반 톤 조정
        if user_profile and hasattr(user_profile, 'conversation_style'):
            if user_profile.conversation_style == 'casual':
                return ResponseTone.CASUAL
            elif user_profile.conversation_style == 'excited':
                return ResponseTone.EXCITED

        # 의도별 기본 톤
        tone_mapping = {
            IntentType.FOOD_REQUEST: ResponseTone.FRIENDLY,
            IntentType.BUDGET_INQUIRY: ResponseTone.FRIENDLY,
            IntentType.LOCATION_INQUIRY: ResponseTone.FRIENDLY,
            IntentType.TIME_INQUIRY: ResponseTone.FRIENDLY,
            IntentType.COUPON_INQUIRY: ResponseTone.EXCITED,
            IntentType.GENERAL_CHAT: ResponseTone.FRIENDLY,
            IntentType.GOODBYE: ResponseTone.FRIENDLY
        }

        return tone_mapping.get(intent, self.default_tone)

    def _generate_main_response(
            self,
            intent: IntentType,
            entities: Dict[str, Any],
            recommendations: List[Dict],
            tone: ResponseTone
    ) -> str:
        """메인 응답 생성"""

        # 의도별 응답 생성
        if intent == IntentType.FOOD_REQUEST:
            return self._generate_food_response(entities, recommendations, tone)
        elif intent == IntentType.BUDGET_INQUIRY:
            return self._generate_budget_response(entities, recommendations, tone)
        elif intent == IntentType.LOCATION_INQUIRY:
            return self._generate_location_response(entities, recommendations, tone)
        elif intent == IntentType.TIME_INQUIRY:
            return self._generate_time_response(entities, recommendations, tone)
        elif intent == IntentType.COUPON_INQUIRY:
            return self._generate_coupon_response(entities, recommendations, tone)
        elif intent == IntentType.GENERAL_CHAT:
            return self._generate_general_response(entities, tone)
        else:
            return self._generate_fallback_response(tone)

    def _generate_food_response(
            self,
            entities: Dict[str, Any],
            recommendations: List[Dict],
            tone: ResponseTone
    ) -> str:
        """음식 추천 응답 생성"""

        if not recommendations:
            # 추천할 음식이 없는 경우
            templates = self.response_templates[IntentType.FOOD_REQUEST]['no_specific_food']
            return random.choice(templates.templates)

        # 첫 번째 추천 사용
        rec = recommendations[0]

        # 착한가게인지 확인
        if rec.get('is_good_influence_shop', False):
            templates = self.response_templates[IntentType.FOOD_REQUEST]['good_influence_shop']
            template = random.choice(templates.templates)

            return template.format(
                shop_name=rec.get('shop_name', ''),
                menu_name=rec.get('menu_name', ''),
                price=rec.get('price', 0)
            )
        else:
            templates = self.response_templates[IntentType.FOOD_REQUEST]['with_recommendations']
            template = random.choice(templates.templates)

            return template.format(
                food_type=entities.get('food_type', '음식'),
                shop_name=rec.get('shop_name', ''),
                menu_name=rec.get('menu_name', ''),
                price=rec.get('price', 0)
            )

    def _generate_budget_response(
            self,
            entities: Dict[str, Any],
            recommendations: List[Dict],
            tone: ResponseTone
    ) -> str:
        """예산 관련 응답 생성"""

        budget = entities.get('budget', 0)
        food_type = entities.get('food_type', '')

        # 음식명과 예산이 함께 있는 경우 (예: "치킨 5000원")
        if food_type and recommendations:
            # 음식 추천 스타일로 응답
            rec = recommendations[0]
            return f"{food_type} {budget}원으로 드시고 싶으시군요! {rec.get('shop_name', '')}의 {rec.get('menu_name', '')}({rec.get('price', 0)}원) 어떠세요?"

        if not recommendations:
            # 예산 내 메뉴가 없는 경우
            if food_type:
                return f"{food_type} {budget}원으로는 조금 어려워요 ㅠㅠ 하지만 {budget + 2000}원 정도면 좋은 {food_type} 드실 수 있어요!"
            else:
                templates = self.response_templates[IntentType.BUDGET_INQUIRY]['over_budget']
                template = random.choice(templates.templates)
                return template.format(
                    budget=budget,
                    alternative_budget=budget + 2000,
                    menu_list="김치찌개, 라면"
                )

        # 예산 내 메뉴가 있는 경우
        menu_list = ", ".join([rec.get('menu_name', '') for rec in recommendations[:3]])

        templates = self.response_templates[IntentType.BUDGET_INQUIRY]['within_budget']
        template = random.choice(templates.templates)

        return template.format(
            budget=budget,
            menu_list=menu_list,
            menu_count=len(recommendations)
        )

    def _generate_location_response(
            self,
            entities: Dict[str, Any],
            recommendations: List[Dict],
            tone: ResponseTone
    ) -> str:
        """위치 관련 응답 생성"""

        if not recommendations:
            templates = self.response_templates[IntentType.LOCATION_INQUIRY]['no_nearby']
            template = random.choice(templates.templates)

            return template.format(
                shop_name="좋은 가게",
                transport_method="버스",
                time="10",
                alternative_location="역 주변"
            )

        rec = recommendations[0]
        templates = self.response_templates[IntentType.LOCATION_INQUIRY]['nearby_shops']
        template = random.choice(templates.templates)

        return template.format(
            shop_name=rec.get('shop_name', ''),
            distance="5",
            location=entities.get('location_preference', '근처'),
            walking_time="5분",
            address=rec.get('address', '')
        )

    def _generate_time_response(
            self,
            entities: Dict[str, Any],
            recommendations: List[Dict],
            tone: ResponseTone
    ) -> str:
        """시간/운영시간 응답 생성"""

        if not recommendations:
            return "운영시간 정보를 확인할 수 없어요 ㅠㅠ 다른 가게 알아볼까요?"

        rec = recommendations[0]
        current_status = rec.get('current_status', 'UNKNOWN')

        if current_status == 'OPEN':
            templates = self.response_templates[IntentType.TIME_INQUIRY]['currently_open']
            template = random.choice(templates.templates)
            return template.format(
                shop_name=rec.get('shop_name', ''),
                close_time=rec.get('close_hour', '밤늦게')
            )
        elif current_status == 'CLOSED':
            templates = self.response_templates[IntentType.TIME_INQUIRY]['currently_closed']
            template = random.choice(templates.templates)
            return template.format(
                shop_name=rec.get('shop_name', ''),
                open_time=rec.get('open_hour', '내일'),
                close_time=rec.get('close_hour', '')
            )
        else:  # BREAK
            templates = self.response_templates[IntentType.TIME_INQUIRY]['break_time']
            template = random.choice(templates.templates)
            return template.format(
                shop_name=rec.get('shop_name', ''),
                break_end_time=rec.get('break_end_hour', '조금 후')
            )

    def _generate_coupon_response(
            self,
            entities: Dict[str, Any],
            recommendations: List[Dict],
            tone: ResponseTone
    ) -> str:
        """쿠폰 관련 응답 생성"""

        if not recommendations:
            return "지금은 사용 가능한 쿠폰이 없어요 ㅠㅠ 나중에 다시 확인해보세요!"

        coupon = recommendations[0]

        if coupon.get('min_amount'):
            templates = self.response_templates[IntentType.COUPON_INQUIRY]['coupon_conditions']
            template = random.choice(templates.templates)
            return template.format(
                coupon_name=coupon.get('name', '할인쿠폰'),
                min_amount=coupon.get('min_amount', 0),
                discount_amount=coupon.get('amount', 0)
            )
        else:
            templates = self.response_templates[IntentType.COUPON_INQUIRY]['available_coupons']
            template = random.choice(templates.templates)
            return template.format(
                coupon_name=coupon.get('name', '할인쿠폰'),
                discount_amount=coupon.get('amount', 0)
            )

    def _generate_general_response(self, entities: Dict[str, Any], tone: ResponseTone) -> str:
        """일반 대화 응답 생성"""

        # 간단한 키워드 기반 분류
        raw_text = entities.get('raw_text', '').lower()

        # 음식명이 포함되어 있으면 음식 추천으로 유도
        food_keywords = ['치킨', '피자', '햄버거', '파스타', '한식', '중식', '일식', '양식', '분식', '김치찌개', '된장찌개', '라면', '떡볶이', '짜장면', '짬뽕', '탕수육', '초밥', '돈까스', '카레']
        if any(food in raw_text for food in food_keywords):
            # 음식명이 있으면 음식 추천 모드로 전환
            detected_food = next(food for food in food_keywords if food in raw_text)
            return f"{detected_food} 드시고 싶으시군요! 좋은 곳 찾아드릴게요! 예산은 얼마 정도로 생각하고 계세요?"

        if any(word in raw_text for word in ['안녕', '하이', '헬로']):
            templates = self.response_templates[IntentType.GENERAL_CHAT]['greeting']
        elif any(word in raw_text for word in ['고마워', '감사', 'ㄱㅅ']):
            templates = self.response_templates[IntentType.GENERAL_CHAT]['thanks']
        elif any(word in raw_text for word in ['맛있었', '좋았', '만족']):
            templates = self.response_templates[IntentType.GENERAL_CHAT]['positive_feedback']
        else:
            templates = self.response_templates[IntentType.GENERAL_CHAT]['greeting']

        return random.choice(templates.templates)

    def _generate_fallback_response(self, tone: ResponseTone) -> str:
        """폴백 응답 생성"""
        fallback_responses = [
            "죄송해요, 잘 이해하지 못했어요 ㅠㅠ 다시 말씀해주시겠어요?",
            "음.. 무슨 말씀인지 잘 모르겠어요. 음식 관련해서 도와드릴까요?",
            "헷갈리네요! 간단하게 말씀해주시면 더 잘 도와드릴 수 있어요!",
            "이해하기 어려워요 ㅠㅠ 예를 들어 '치킨 추천해줘' 이런 식으로 말씀해주세요!"
        ]

        return random.choice(fallback_responses)

    def _generate_additional_info(
            self,
            intent: IntentType,
            entities: Dict[str, Any],
            recommendations: List[Dict],
            user_profile: UserProfile = None
    ) -> str:
        """추가 정보 생성"""

        additional_info = []

        # 착한가게 정보 추가
        if recommendations:
            good_shops = [r for r in recommendations if r.get('is_good_influence_shop', False)]
            if good_shops and intent != IntentType.COUPON_INQUIRY:
                additional_info.append("참고로 착한가게에서 드시면 지역사회에도 도움이 돼요! ✨")

        # 할인 정보 추가
        if intent == IntentType.BUDGET_INQUIRY and recommendations:
            discount_shops = [r for r in recommendations if r.get('ordinary_discount', False)]
            if discount_shops:
                additional_info.append("할인도 받을 수 있는 곳들이에요!")

        # 사용자 프로필 기반 추가 정보
        if user_profile and hasattr(user_profile, 'preferred_categories'):
            if user_profile.preferred_categories and intent == IntentType.FOOD_REQUEST:
                fav_category = user_profile.preferred_categories[0]
                additional_info.append(f"평소 {fav_category} 좋아하시니까 입맛에 맞을 거예요!")

        return " ".join(additional_info)

    def _generate_follow_up_questions(
            self,
            intent: IntentType,
            entities: Dict[str, Any],
            recommendations: List[Dict]
    ) -> List[str]:
        """후속 질문 생성"""

        follow_ups = []

        if intent == IntentType.FOOD_REQUEST:
            if not entities.get('budget'):
                follow_ups.append("예산은 어느 정도 생각하고 계세요?")
            if not entities.get('companions'):
                follow_ups.append("혼자 드실 건가요, 아니면 누구와 함께요?")
            if recommendations and len(recommendations) > 1:
                follow_ups.append("다른 옵션도 보실까요?")

        elif intent == IntentType.BUDGET_INQUIRY:
            if recommendations:
                follow_ups.append("이 중에서 어떤 메뉴가 관심 있으세요?")
                follow_ups.append("위치는 어디쯤이 좋으세요?")

        elif intent == IntentType.LOCATION_INQUIRY:
            if recommendations:
                follow_ups.append("길찾기 도움이 필요하세요?")
                follow_ups.append("운영시간도 확인해드릴까요?")

        elif intent == IntentType.TIME_INQUIRY:
            follow_ups.append("다른 시간대는 어떠세요?")
            follow_ups.append("대안으로 다른 가게도 알아볼까요?")

        return follow_ups[:2]  # 최대 2개까지만

    def _combine_response_parts(self, main_response: str, additional_info: str, tone: ResponseTone) -> str:
        """응답 부분들 조합"""

        response_parts = [main_response]

        if additional_info:
            response_parts.append(additional_info)

        # 톤에 따른 이모티콘 추가
        if tone in self.emoticons and random.random() < 0.3:  # 30% 확률로 이모티콘 추가
            emoticon = random.choice(self.emoticons[tone])
            response_parts.append(emoticon)

        return " ".join(response_parts)

    def _needs_action(self, intent: IntentType) -> bool:
        """추가 액션이 필요한지 판단"""
        action_required_intents = {
            IntentType.FOOD_REQUEST,
            IntentType.BUDGET_INQUIRY,
            IntentType.LOCATION_INQUIRY,
            IntentType.TIME_INQUIRY,
            IntentType.COUPON_INQUIRY
        }

        return intent in action_required_intents

    def add_personality(self, response: str, user_profile: UserProfile = None) -> str:
        """사용자 성향에 맞는 개성 추가"""

        if not user_profile:
            return response

        # 대화 스타일에 따른 개성 추가
        style = getattr(user_profile, 'conversation_style', 'friendly')

        if style == 'casual':
            # 캐주얼한 표현 추가
            casual_additions = ['ㅋㅋ', 'ㅎㅎ', '^^', '~']
            if not any(add in response for add in casual_additions):
                response += f" {random.choice(casual_additions)}"

        elif style == 'excited':
            # 신나는 표현 추가
            if '!' not in response:
                response = response.replace('.', '!')
            excited_additions = ['대박!', '완전!', '짱!']
            response += f" {random.choice(excited_additions)}"

        elif style == 'polite':
            # 정중한 표현으로 변환
            response = response.replace('해요', '합니다')
            response = response.replace('드세요', '드시기 바랍니다')

        return response

    def generate_owner_message_response(self, shop: NaviyamShop) -> str:
        """사장님 메시지 기반 응답 생성"""

        if not shop.owner_message:
            return ""

        message_responses = [
            f"사장님이 '{shop.owner_message}'라고 하시네요!",
            f"가게 사장님 말씀: '{shop.owner_message}'",
            f"사장님이 직접 '{shop.owner_message}'라고 말씀하셨어요!",
            f"'{shop.owner_message}' - 사장님이 자신만만하게 추천하시네요!"
        ]

        return random.choice(message_responses)

    def generate_coupon_explanation(self, coupon: NaviyamCoupon) -> str:
        """쿠폰 설명 생성"""

        explanation_parts = []

        # 기본 할인 정보
        explanation_parts.append(f"{coupon.amount}원 할인")

        # 최소 주문 금액
        if coupon.min_amount:
            explanation_parts.append(f"{coupon.min_amount}원 이상 주문시")

        # 사용처 제한
        if coupon.usage_type == "SHOP":
            explanation_parts.append("포장방문에서만 사용 가능")
        elif coupon.usage_type == "PRODUCT":
            explanation_parts.append("배송상품에서만 사용 가능")

        # 대상 제한
        if "FOOD_CARD" in coupon.target:
            explanation_parts.append("결식아동 대상")
        elif "TEENAGER" in coupon.target:
            explanation_parts.append("10대 대상")

        return ", ".join(explanation_parts)

    def generate_menu_option_response(self, menu: NaviyamMenu, requested_options: List[str]) -> str:
        """메뉴 옵션 관련 응답 생성"""

        if not menu.options:
            return f"{menu.name}는 기본 메뉴로만 가능해요!"

        # 요청된 옵션과 매칭
        available_options = []
        for option in menu.options:
            option_name = option.get('name', '')
            for requested in requested_options:
                if requested in option_name.lower():
                    price_info = f"+{option.get('additional_price', 0)}원" if option.get('additional_price',
                                                                                        0) > 0 else ""
                    available_options.append(f"{option_name} {price_info}".strip())

        if available_options:
            return f"{menu.name}에 {', '.join(available_options)} 옵션 가능해요!"
        else:
            # 요청 옵션은 없지만 다른 옵션들 안내
            other_options = [opt.get('name', '') for opt in menu.options[:3]]
            return f"{menu.name}는 {', '.join(other_options)} 등의 옵션이 있어요!"

    def generate_comparison_response(self, shops: List[NaviyamShop], comparison_criteria: str) -> str:
        """가게 비교 응답 생성"""

        if len(shops) < 2:
            return "비교할 가게가 충분하지 않아요!"

        shop1, shop2 = shops[0], shops[1]

        if comparison_criteria == "price":
            return f"{shop1.name}과 {shop2.name} 중에서는 가격대가 비슷해요! 둘 다 좋은 선택이에요."

        elif comparison_criteria == "distance":
            return f"거리상으로는 {shop1.name}이 조금 더 가까워요! 하지만 {shop2.name}도 멀지 않아요."

        elif comparison_criteria == "good_influence":
            good_shops = [s for s in [shop1, shop2] if s.is_good_influence_shop]
            if good_shops:
                good_shop = good_shops[0]
                return f"{good_shop.name}는 착한가게라서 더 의미있는 선택이 될 것 같아요!"
            else:
                return f"{shop1.name}과 {shop2.name} 모두 좋은 가게예요!"

        return f"{shop1.name}과 {shop2.name} 둘 다 추천드려요! 기분에 따라 선택해보세요!"

    def generate_seasonal_recommendation(self, season: str, shops: List[NaviyamShop]) -> str:
        """계절별 추천 응답 생성"""

        seasonal_messages = {
            "spring": "따뜻한 봄날에는 가볍게 드실 수 있는",
            "summer": "더운 여름에는 시원하고 아삭한",
            "fall": "선선한 가을에는 따뜻하고 든든한",
            "winter": "추운 겨울에는 뜨끈뜨끈한"
        }

        seasonal_foods = {
            "spring": ["비빔밥", "샐러드", "냉면"],
            "summer": ["냉면", "물냉면", "빙수"],
            "fall": ["찌개", "국밥", "전골"],
            "winter": ["찌개", "국밥", "탕", "라면"]
        }

        message = seasonal_messages.get(season, "오늘 같은 날에는")
        foods = seasonal_foods.get(season, ["맛있는 음식"])

        if shops:
            shop_name = shops[0].name
            return f"{message} {random.choice(foods)} 어떠세요? {shop_name}에서 맛있게 드실 수 있어요!"
        else:
            return f"{message} {random.choice(foods)} 찾아드릴까요?"

    def generate_group_recommendation(self, companion_count: int, shops: List[NaviyamShop]) -> str:
        """인원수별 추천 응답 생성"""

        if companion_count == 1:  # 혼자
            return f"혼밥도 좋죠! {shops[0].name if shops else '좋은 곳'}에서 편안하게 드세요!"

        elif companion_count == 2:  # 2명
            return f"둘이서 드시기 좋은 곳이에요! {shops[0].name if shops else '추천 가게'}에서 맛있게 드세요!"

        elif companion_count <= 4:  # 3-4명
            return f"친구들과 함께 가기 딱 좋네요! {shops[0].name if shops else '좋은 가게'}는 단체로 가기에도 좋아요!"

        else:  # 5명 이상
            return f"큰 모임이시네요! {shops[0].name if shops else '추천 가게'}에 미리 연락해서 자리 확인해보시는 게 좋을 것 같아요!"

    def generate_emergency_response(self, situation: str) -> str:
        """응급 상황 응답 생성"""

        emergency_responses = {
            "all_closed": "아이고... 지금 시간에는 대부분 문 닫았네요 ㅠㅠ 편의점이나 24시간 가게 찾아보시는 건 어떨까요?",
            "no_budget_match": "예산에 맞는 곳을 찾기 어렵네요... 조금만 더 올려주시거나 간단한 분식은 어떠세요?",
            "no_restaurants": "근처에 음식점이 없는 것 같아요 ㅠㅠ 조금 더 넓은 범위로 찾아볼까요?",
            "system_error": "죄송해요! 잠시 문제가 있는 것 같아요. 조금 후에 다시 시도해주세요!"
        }

        return emergency_responses.get(situation, "죄송해요, 도움을 드리기 어려운 상황이에요 ㅠㅠ")


# 편의 함수들
def quick_response_generation(
        intent: IntentType,
        entities: Dict[str, Any],
        recommendations: List[Dict] = None
) -> str:
    """빠른 응답 생성 (편의 함수)"""
    nlg = NaviyamNLG()
    response = nlg.generate_response(intent, entities, recommendations)
    return response.text


def generate_personalized_response(
        intent: IntentType,
        entities: Dict[str, Any],
        recommendations: List[Dict],
        user_profile: UserProfile
) -> ChatbotResponse:
    """개인화된 응답 생성 (편의 함수)"""
    nlg = NaviyamNLG()
    response = nlg.generate_response(intent, entities, recommendations, user_profile)

    # 개성 추가
    response.text = nlg.add_personality(response.text, user_profile)

    return response


def generate_multi_recommendation_response(
        recommendations: List[Dict],
        max_recommendations: int = 3
) -> str:
    """다중 추천 응답 생성 (편의 함수)"""
    if not recommendations:
        return "추천할 만한 곳을 찾지 못했어요 ㅠㅠ"

    if len(recommendations) == 1:
        rec = recommendations[0]
        return f"{rec.get('shop_name', '')}의 {rec.get('menu_name', '')} 추천드려요!"

    # 여러 개 추천
    rec_texts = []
    for i, rec in enumerate(recommendations[:max_recommendations]):
        rec_texts.append(f"{i + 1}. {rec.get('shop_name', '')} - {rec.get('menu_name', '')} ({rec.get('price', 0)}원)")

    return f"몇 가지 추천드릴게요!\n" + "\n".join(rec_texts) + "\n어떤 게 관심 있으세요?"