"""
나비얌 챗봇 데이터 구조 정의
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class IntentType(Enum):
    """의도 분류 열거형"""
    FOOD_REQUEST = "food_request"  # 음식 추천 요청
    BUDGET_INQUIRY = "budget_inquiry"  # 예산 관련 질문
    LOCATION_INQUIRY = "location_inquiry"  # 위치 관련 질문
    TIME_INQUIRY = "time_inquiry"  # 시간/운영시간 질문
    COUPON_INQUIRY = "coupon_inquiry"  # 쿠폰/할인 관련
    MENU_OPTION = "menu_option"  # 메뉴 옵션 (맵기, 양 등)
    GENERAL_CHAT = "general_chat"  # 일반 대화
    GOODBYE = "goodbye"  # 대화 종료


class ConfidenceLevel(Enum):
    """신뢰도 수준"""
    HIGH = "high"  # 0.8 이상
    MEDIUM = "medium"  # 0.5-0.8
    MEDIUM_LOW = 'medium_low' # 0.3 ~ 0.5
    LOW = "low"  # 0.5 미만
    VERY_LOW = 'very_low' # 0.2 미만


@dataclass
class UserInput:
    """사용자 입력 데이터"""
    text: str  # 원본 사용자 입력
    user_id: str  # 사용자 ID
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""  # 대화 세션 ID

    def __post_init__(self):
        if not self.session_id:
            self.session_id = f"{self.user_id}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"


@dataclass
class NaviyamShop:
    """나비얌 가게 정보"""
    id: int
    name: str
    category: str
    is_good_influence_shop: bool  # 착한가게 여부
    is_food_card_shop: str  # 푸드카드 사용 가능 여부
    address: str
    open_hour: str
    close_hour: str
    break_start_hour: Optional[str] = None
    break_end_hour: Optional[str] = None
    current_status: str = "UNKNOWN"  # OPEN, CLOSED, BREAK
    owner_message: Optional[str] = None
    ordinary_discount: bool = False  # 일반 할인 제공 여부


@dataclass
class NaviyamMenu:
    """나비얌 메뉴 정보"""
    id: int
    shop_id: int
    name: str
    price: int
    description: Optional[str] = None
    category: Optional[str] = None
    is_popular: bool = False  # 인기 메뉴 여부
    options: List[Dict] = field(default_factory=list)  # 메뉴 옵션들


@dataclass
class NaviyamCoupon:
    """나비얌 쿠폰 정보"""
    id: str
    name: str
    description: str
    amount: int  # 할인 금액
    min_amount: Optional[int] = None  # 최소 주문 금액
    usage_type: str = "ALL"  # ALL, SHOP, PRODUCT
    target: List[str] = field(default_factory=lambda: ["ALL"])
    applicable_shops: List[int] = field(default_factory=list)


@dataclass
class ExtractedEntity:
    """추출된 엔티티 정보"""
    food_type: Optional[str] = None  # 음식 종류 (치킨, 한식 등)
    budget: Optional[int] = None  # 예산 (원 단위)
    location_preference: Optional[str] = None  # 지역 선호 (근처, 강남 등)
    companions: List[str] = field(default_factory=list)  # 동반자 (친구, 가족)
    time_preference: Optional[str] = None  # 시간 선호 (지금, 저녁)
    menu_options: List[str] = field(default_factory=list)  # 메뉴 옵션 (맵게, 곱배기)
    special_requirements: List[str] = field(default_factory=list)  # 특별 요구사항


@dataclass
class ExtractedInfo:
    """챗봇이 추출한 구조화 정보"""
    intent: IntentType
    entities: ExtractedEntity
    confidence: float  # 추출 신뢰도 (0.0-1.0)
    confidence_level: ConfidenceLevel
    raw_text: str  # 원본 텍스트

    def __post_init__(self):
        # 신뢰도 수준 자동 설정
        if self.confidence >= 0.8:
            self.confidence_level = ConfidenceLevel.HIGH
        elif self.confidence >= 0.5:
            self.confidence_level = ConfidenceLevel.MEDIUM
        elif self.confidence >= 0.3:
            self.confidence_level = ConfidenceLevel.MEDIUM_LOW  # 추가
        elif self.confidence >= 0.2:
            self.confidence_level = ConfidenceLevel.LOW
        else:
            self.confidence_level = ConfidenceLevel.VERY_LOW

@dataclass
class UserProfile:
    """사용자 프로필 (개인화용)"""
    user_id: str
    preferred_categories: List[str] = field(default_factory=list)  # 선호 음식 카테고리
    average_budget: Optional[int] = None  # 평균 예산
    favorite_shops: List[int] = field(default_factory=list)  # 즐겨찾는 가게
    recent_orders: List[Dict] = field(default_factory=list)  # 최근 주문 이력
    conversation_style: str = "friendly"  # 대화 스타일
    last_updated: datetime = field(default_factory=datetime.now)

    def update_preferences(self, new_order: Dict):
        """새로운 주문 정보로 선호도 업데이트"""
        self.recent_orders.append(new_order)
        # 최근 10개만 유지
        if len(self.recent_orders) > 10:
            self.recent_orders = self.recent_orders[-10:]
        self.last_updated = datetime.now()

    taste_preferences: Dict[str, float] = field(default_factory=dict)  # {"매운맛": 0.3, "짠맛": 0.8}
    companion_patterns: List[str] = field(default_factory=list)  # ["친구", "혼자", "가족"]
    location_preferences: List[str] = field(default_factory=list)  # ["건국대", "강남"]
    good_influence_preference: float = 0.5  # 착한가게 선호도
    interaction_count: int = 0  # 총 상호작용 횟수
    data_completeness: float = 0.0  # 데이터 완성도 (0.0 ~ 1.0)


@dataclass
class ChatbotResponse:
    """챗봇 응답 데이터"""
    text: str  # 사용자에게 보여줄 응답 텍스트
    recommendations: List[Dict] = field(default_factory=list)  # 추천 결과
    follow_up_questions: List[str] = field(default_factory=list)  # 후속 질문
    action_required: bool = False  # 추가 액션 필요 여부
    metadata: Dict[str, Any] = field(default_factory=dict)  # 메타데이터


@dataclass
class ChatbotOutput:
    """챗봇 최종 출력"""
    response: ChatbotResponse
    extracted_info: ExtractedInfo  # 추천 시스템용 구조화 데이터
    learning_data: Dict = field(default_factory=dict)  # 개인화 학습용 데이터
    session_data: Dict = field(default_factory=dict)  # 세션 유지 데이터


@dataclass
class TrainingData:
    """학습 데이터 구조"""
    input_text: str  # 입력 텍스트
    target_intent: IntentType  # 정답 의도
    target_entities: ExtractedEntity  # 정답 엔티티
    expected_response: str  # 기대 응답
    domain: str = "naviyam"  # 도메인


@dataclass
class NaviyamKnowledge:
    """나비얌 도메인 지식베이스"""
    shops: Dict[int, NaviyamShop] = field(default_factory=dict)
    menus: Dict[int, NaviyamMenu] = field(default_factory=dict)
    coupons: Dict[str, NaviyamCoupon] = field(default_factory=dict)
    reviews: List[Dict] = field(default_factory=list)
    popular_combinations: List[Dict] = field(default_factory=list)  # 인기 조합

    def get_good_influence_shops(self) -> List[NaviyamShop]:
        """착한가게 목록 반환"""
        return [shop for shop in self.shops.values() if shop.is_good_influence_shop]

    def get_shops_by_category(self, category: str) -> List[NaviyamShop]:
        """카테고리별 가게 목록 반환"""
        return [shop for shop in self.shops.values() if shop.category == category]

    def get_menus_in_budget(self, max_budget: int) -> List[NaviyamMenu]:
        """예산 내 메뉴 목록 반환"""
        return [menu for menu in self.menus.values() if menu.price <= max_budget]


@dataclass
class UserState:
    """사용자 상태 정보"""
    strategy: str  # "onboarding_mode", "data_building_mode", "normal_mode"
    data_completeness: float  # 0.0 ~ 1.0
    interaction_count: int
    last_interaction: datetime = field(default_factory=datetime.now)


@dataclass
class LearningData:
    """수집된 학습 데이터"""
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)

    # 기본 추출 데이터
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    intent_confidence: float = 0.0

    # 학습용 Feature들
    food_preferences: List[str] = field(default_factory=list)
    budget_patterns: List[int] = field(default_factory=list)
    companion_patterns: List[str] = field(default_factory=list)
    taste_preferences: Dict[str, float] = field(default_factory=dict)

    # 선택/피드백 데이터
    recommendations_provided: List[Dict] = field(default_factory=list)
    user_selection: Optional[Dict] = None
    user_feedback: Optional[str] = None
    satisfaction_score: Optional[float] = None

# 전역 상수
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
MAX_RESPONSE_LENGTH = 200
MAX_CONVERSATION_HISTORY = 10