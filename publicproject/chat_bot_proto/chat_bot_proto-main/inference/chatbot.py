"""
나비얌 메인 챗봇 클래스
전체 대화 플로우 관리 및 모듈 통합
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict
import json
from pathlib import Path

from data.data_structure import (
    UserInput, ChatbotOutput, ChatbotResponse, ExtractedInfo, ExtractedEntity,
    UserProfile, NaviyamKnowledge, IntentType, ConfidenceLevel, UserState, LearningData
)
from data.data_loader import NaviyamDataLoader
from models.model_factory import create_model, ModelSelection
from models.models_config import ModelConfigManager
from nlp.preprocessor import NaviyamTextPreprocessor, EmotionType
from nlp.nlu import NaviyamNLU
from nlp.nlg import NaviyamNLG, ResponseTone
from nlp.llm_normalizer import LLMNormalizer, LLMNormalizedOutput
from .user_manager import NaviyamUserManager
from .response_generator import NaviyamResponseGenerator
from rag.retriever import create_naviyam_retriever

logger = logging.getLogger(__name__)


class ConversationMemory:
    """대화 메모리 관리"""

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations = {}  # user_id -> conversation_history

    def add_conversation(self, user_id: str, user_input: str, bot_response: str, extracted_info: ExtractedInfo):
        """대화 추가"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        conversation_item = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response,
            "intent": extracted_info.intent.value,
            "confidence": extracted_info.confidence,
            "entities": asdict(extracted_info.entities)
        }

        self.conversations[user_id].append(conversation_item)

        # 최대 히스토리 유지
        if len(self.conversations[user_id]) > self.max_history:
            self.conversations[user_id] = self.conversations[user_id][-self.max_history:]

    def get_recent_conversations(self, user_id: str, count: int = 3) -> List[Dict]:
        """최근 대화 조회"""
        if user_id not in self.conversations:
            return []
        return self.conversations[user_id][-count:]

    def clear_conversations(self, user_id: str = None):
        """대화 기록 삭제"""
        if user_id:
            self.conversations.pop(user_id, None)
        else:
            self.conversations.clear()


class PerformanceMonitor:
    """성능 모니터링"""

    def __init__(self):
        self.metrics = {
            "total_conversations": 0,
            "total_response_time": 0.0,
            "avg_response_time": 0.0,
            "intent_accuracy": 0.0,
            "user_satisfaction": 0.0,
            "error_count": 0,
            "successful_recommendations": 0
        }
        self.response_times = []

    def record_conversation(self, response_time: float, success: bool = True):
        """대화 기록"""
        self.metrics["total_conversations"] += 1
        self.metrics["total_response_time"] += response_time
        self.response_times.append(response_time)

        if success:
            self.metrics["successful_recommendations"] += 1
        else:
            self.metrics["error_count"] += 1

        # 평균 응답 시간 계산
        if self.metrics["total_conversations"] > 0:
            self.metrics["avg_response_time"] = (
                    self.metrics["total_response_time"] / self.metrics["total_conversations"]
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 반환"""
        recent_times = self.response_times[-100:] if len(self.response_times) > 100 else self.response_times

        summary = self.metrics.copy()
        if recent_times:
            summary["recent_avg_response_time"] = sum(recent_times) / len(recent_times)
            summary["recent_max_response_time"] = max(recent_times)
            summary["recent_min_response_time"] = min(recent_times)

        summary["success_rate"] = (
                self.metrics["successful_recommendations"] / max(self.metrics["total_conversations"], 1)
        )

        return summary


class NaviyamChatbot:
    """나비얌 메인 챗봇"""

    def __init__(self, config):
        """
        Args:
            config: AppConfig 객체
        """
        self.config = config

        # 핵심 컴포넌트들
        self.knowledge: Optional[NaviyamKnowledge] = None
        self.model = None  # A.X 3.1 Lite 또는 KoAlpaca 모델
        self.preprocessor: Optional[NaviyamTextPreprocessor] = None
        self.nlu: Optional[NaviyamNLU] = None
        self.nlg: Optional[NaviyamNLG] = None
        self.user_manager: Optional[NaviyamUserManager] = None
        self.response_generator: Optional[NaviyamResponseGenerator] = None
        self.llm_normalizer: Optional[LLMNormalizer] = None
        self.data_collector = None

        # 메모리 및 모니터링
        self.conversation_memory = ConversationMemory(config.data.max_conversations)
        self.performance_monitor = PerformanceMonitor()

        # 상태 관리
        self.is_initialized = False
        self.last_cleanup_time = datetime.now()

        # 초기화
        self._initialize_components()

    def _initialize_components(self):
        """컴포넌트 초기화 (상세 성능 측정 포함)"""
        try:
            logger.info("나비얌 챗봇 초기화 시작...")
            total_start = time.time()

            # 1. 데이터 로드
            step_start = time.time()
            self._load_knowledge_base()
            kb_time = time.time() - step_start
            logger.info(f"[측정] 지식베이스 로드: {kb_time:.3f}초")

            # 2. 모델 로드 (선택적)
            if self.config.model and hasattr(self.config.model, 'model_name'):
                step_start = time.time()
                self._load_language_model()
                llm_time = time.time() - step_start
                logger.info(f"[측정] LLM 모델 로드: {llm_time:.3f}초")
            else:
                llm_time = 0.0

            # 3. NLP 컴포넌트 초기화
            step_start = time.time()
            self._initialize_nlp_components()
            nlp_time = time.time() - step_start
            logger.info(f"[측정] NLP 컴포넌트 초기화: {nlp_time:.3f}초")

            # 4. 응답 생성기 초기화
            step_start = time.time()
            self._initialize_response_components()
            response_time = time.time() - step_start
            logger.info(f"[측정] 응답 생성기 초기화: {response_time:.3f}초")

            # 5. 사용자 관리자 초기화
            step_start = time.time()
            self._initialize_user_manager()
            user_mgr_time = time.time() - step_start
            logger.info(f"[측정] 사용자 관리자 초기화: {user_mgr_time:.3f}초")

            # 6. RAG 시스템 초기화
            step_start = time.time()
            self._initialize_rag_system()
            rag_time = time.time() - step_start
            logger.info(f"[측정] RAG 시스템 초기화: {rag_time:.3f}초")

            total_time = time.time() - total_start
            
            # 성능 분석 리포트
            logger.info("=" * 50)
            logger.info("🚀 Phase 3 성능 측정 리포트")
            logger.info("=" * 50)
            logger.info(f"총 초기화 시간: {total_time:.3f}초")
            logger.info(f"📊 컴포넌트별 소요 시간:")
            logger.info(f"  • LLM 모델 로드:     {llm_time:.3f}초 ({llm_time/total_time*100:.1f}%)")
            logger.info(f"  • RAG 시스템:       {rag_time:.3f}초 ({rag_time/total_time*100:.1f}%)")
            logger.info(f"  • 지식베이스:       {kb_time:.3f}초 ({kb_time/total_time*100:.1f}%)")
            logger.info(f"  • NLP 컴포넌트:     {nlp_time:.3f}초 ({nlp_time/total_time*100:.1f}%)")
            logger.info(f"  • 응답 생성기:       {response_time:.3f}초 ({response_time/total_time*100:.1f}%)")
            logger.info(f"  • 사용자 관리자:     {user_mgr_time:.3f}초 ({user_mgr_time/total_time*100:.1f}%)")
            logger.info("=" * 50)
            
            if total_time > 3.0:
                logger.warning(f"⚠️  3초 목표 미달성! {total_time-3.0:.3f}초 추가 최적화 필요")
            else:
                logger.info(f"✅ 3초 목표 달성! ({3.0-total_time:.3f}초 여유)")

            self.is_initialized = True

        except Exception as e:
            logger.error(f"챗봇 초기화 실패: {e}")
            raise RuntimeError(f"챗봇 초기화 실패: {e}")

    def _load_knowledge_base(self):
        """지식베이스 로드"""
        logger.info("나비얌 지식베이스 로딩...")

        try:
            data_loader = NaviyamDataLoader(self.config.data, self.config.debug)
            self.knowledge = data_loader.load_all_data()

            logger.info(f"지식베이스 로드 완료: "
                        f"가게 {len(self.knowledge.shops)}개, "
                        f"메뉴 {len(self.knowledge.menus)}개")

        except Exception as e:
            logger.error(f"지식베이스 로드 실패: {e}")
            # 빈 지식베이스로 폴백
            self.knowledge = NaviyamKnowledge()

    def _load_language_model(self):
        """언어 모델 로드 (A.X 3.1 Lite 또는 KoAlpaca)"""
        if not self.config.model:
            return

        try:
            # ModelConfig에서 model_type 확인
            model_type = getattr(self.config.model, 'model_type', 'ax')
            model_name = "A.X 3.1 Lite" if model_type == 'ax' else "KoAlpaca"
            
            logger.info(f"{model_name} 모델 로딩...")

            # 모델 팩토리로 모델 생성
            self.model = create_model(
                model_config=self.config.model,
                model_type=model_type,
                cache_dir=self.config.data.cache_dir
            )

            logger.info(f"{model_name} 모델 로드 완료")

        except Exception as e:
            logger.warning(f"언어 모델 로드 실패: {e}. 템플릿 기반으로 동작합니다.")
            self.model = None

    def _initialize_nlp_components(self):
        """NLP 컴포넌트 초기화"""
        logger.info("NLP 컴포넌트 초기화...")

        self.preprocessor = NaviyamTextPreprocessor(preserve_expressions=True)
        self.nlu = NaviyamNLU(use_preprocessor=True)
        self.nlg = NaviyamNLG(default_tone=ResponseTone.FRIENDLY)

        if self.model:
            self.llm_normalizer = LLMNormalizer(self.model)
            logger.info("LLM 정규화기 초기화 완료")

        logger.info("NLP 컴포넌트 초기화 완료")

    def _initialize_response_components(self):
        """응답 생성 컴포넌트 초기화"""
        logger.info("응답 생성기 초기화...")

        self.response_generator = NaviyamResponseGenerator(
            knowledge=self.knowledge,
            nlg=self.nlg,
            model=self.model
        )

        logger.info("응답 생성기 초기화 완료")

    def _initialize_user_manager(self):
        """사용자 관리자 초기화"""
        logger.info("사용자 관리자 초기화...")

        self.user_manager = NaviyamUserManager(
            save_path=str(Path(self.config.data.output_path) / "user_profiles"),
            enable_personalization=self.config.inference.enable_personalization
        )

        logger.info("사용자 관리자 초기화 완료")

    def _initialize_rag_system(self):
        """RAG 시스템 초기화"""
        logger.info("RAG 시스템 초기화...")
        
        try:
            # 설정에서 Vector Store 타입 읽기
            vector_store_type = getattr(self.config, 'rag', None)
            if vector_store_type and hasattr(vector_store_type, 'vector_store_type'):
                store_type = vector_store_type.vector_store_type
                index_path = getattr(vector_store_type, 'index_path', None)
            else:
                store_type = "mock"  # 기본값
                index_path = None
            
            logger.info(f"RAG Vector Store 타입: {store_type}")
            
            # RAG Retriever 생성 (test_data.json 사용)
            if store_type == "faiss" and index_path:
                # FAISS 전용 생성 로직
                from rag.vector_stores import FAISSVectorStore
                from rag.query_parser import QueryStructurizer
                from rag.retriever import NaviyamRetriever, load_knowledge_from_file
                
                # Vector Store 생성
                faiss_store = FAISSVectorStore(
                    embedding_model=None,
                    index_path=index_path
                )
                
                # Query Structurizer 생성
                query_structurizer = QueryStructurizer(llm_client=None)
                
                # Retriever 생성
                self.retriever = NaviyamRetriever(faiss_store, query_structurizer)
                
                # 지식 베이스 로드 및 추가
                knowledge_data = load_knowledge_from_file("rag/test_data.json")
                if knowledge_data:
                    self.retriever.add_knowledge_base(knowledge_data)
                    
                logger.info("FAISS RAG 시스템 초기화 완료")
            else:
                # Mock 또는 기타 타입
                self.retriever = create_naviyam_retriever(
                    knowledge_file_path="rag/test_data.json",
                    vector_store_type=store_type
                )
                logger.info(f"{store_type} RAG 시스템 초기화 완료")
            
        except Exception as e:
            logger.error(f"RAG 시스템 초기화 실패: {e}")
            # RAG 실패 시에도 챗봇이 동작하도록 None으로 설정
            self.retriever = None
            logger.warning("RAG 없이 챗봇 실행")

    def process_user_input(self, user_input: UserInput) -> ChatbotOutput:
        """사용자 입력 처리 (메인 메서드)"""
        if not self.is_initialized:
            raise RuntimeError("챗봇이 초기화되지 않았습니다")

        start_time = time.time()

        try:
            # 1. 입력 검증
            if not user_input.text or not user_input.text.strip():
                return self._generate_empty_input_response(user_input)

            # 2. 전처리
            preprocessed = self.preprocessor.preprocess(user_input.text)

            # 3. 의도 및 엔티티 추출
            # extracted_info = self.nlu.extract_intent_and_entities(
            #     user_input.text, user_input.user_id
            # )
            # 3. 스마트 NLU 처리 (LLM 통합)
            extracted_info = self._smart_nlu_processing(user_input, preprocessed)

            # 3.5. RAG 검색 (추천 관련 의도인 경우)
            rag_context = self._perform_rag_search(user_input, extracted_info)

            # 4. 사용자 프로필 조회/업데이트
            user_profile = self.user_manager.get_or_create_user_profile(user_input.user_id)
            self.user_manager.update_user_interaction(
                user_input.user_id, extracted_info, preprocessed.emotion
            )

            # 5. 응답 생성
            # response = self.response_generator.generate_response(
            #     extracted_info=extracted_info,
            #     user_profile=user_profile,
            #     conversation_context=self.conversation_memory.get_recent_conversations(
            #         user_input.user_id, 3
            #     )
            # )

            # 5. 스마트 응답 생성 (LLM 통합)
            response = self._smart_response_generation(
                extracted_info, user_profile, user_input.user_id, rag_context
            )
            if response.metadata.get("onboarding_complete"):
                # 사용자를 normal_mode로 전환하기 위해 interaction_count 증가
                if user_profile:
                    user_profile.interaction_count = max(user_profile.interaction_count, 3)
                    user_profile.data_completeness = 1.0  # 온보딩 완료로 설정
                    self.user_manager._save_user_profile(user_profile)

                logger.info(f"사용자 {user_input.user_id} 온보딩 완료")
            # 6. 개인화 적용
            response = self.user_manager.personalize_response(response, user_profile)

            # 7. 학습 데이터 수집
            learning_data = self._collect_learning_data(
                user_input, extracted_info, response, preprocessed
            )

            # 8. 데이터 수집기에 전달 (새로 추가)
            if self.data_collector:
                self.data_collector.collect_interaction_data(user_input.user_id, learning_data)

                # 추천 데이터도 수집
                if response.recommendations:
                    self.data_collector.collect_recommendation_data(
                        user_id=user_input.user_id,
                        recommendations=response.recommendations,
                        user_selection=None  # 나중에 사용자 선택시 업데이트
                    )

            # 8. 세션 데이터 생성
            session_data = self._generate_session_data(
                user_input, extracted_info, response
            )

            # 9. 대화 기록 저장
            if self.config.inference.save_conversations:
                self.conversation_memory.add_conversation(
                    user_input.user_id, user_input.text, response.text, extracted_info
                )

            # 10. 성능 모니터링
            response_time = time.time() - start_time
            self.performance_monitor.record_conversation(response_time, True)

            # 11. 메모리 정리 (주기적)
            self._periodic_cleanup()

            return ChatbotOutput(
                response=response,
                extracted_info=extracted_info,
                learning_data=learning_data,
                session_data=session_data
            )

        except Exception as e:
            logger.error(f"사용자 입력 처리 실패: {e}")

            # 에러 응답 생성
            error_response = self._generate_error_response(user_input, str(e))

            response_time = time.time() - start_time
            self.performance_monitor.record_conversation(response_time, False)

            return error_response

    def _generate_empty_input_response(self, user_input: UserInput) -> ChatbotOutput:
        """빈 입력 응답 생성"""
        response = ChatbotResponse(
            text="안녕하세요! 뭐 드시고 싶은지 알려주세요! 😊",
            recommendations=[],
            follow_up_questions=["어떤 음식이 드시고 싶으세요?", "예산은 얼마나 생각하고 계세요?"],
            action_required=False
        )

        return ChatbotOutput(
            response=response,
            extracted_info=ExtractedInfo(
                intent=IntentType.GENERAL_CHAT,
                entities=ExtractedEntity(),
                confidence=1.0,
                raw_text="",
                confidence_level=ConfidenceLevel.HIGH
            ),
            learning_data={},
            session_data={}
        )

    def _generate_error_response(self, user_input: UserInput, error_msg: str) -> ChatbotOutput:
        """에러 응답 생성"""
        response = ChatbotResponse(
            text="죄송해요! 잠시 문제가 있는 것 같아요. 다시 말씀해주시겠어요? 😅",
            recommendations=[],
            follow_up_questions=["간단하게 다시 말씀해주세요!"],
            action_required=False,
            metadata={"error": error_msg}
        )

        return ChatbotOutput(
            response=response,
            extracted_info=ExtractedInfo(
                intent=IntentType.GENERAL_CHAT,
                entities=ExtractedEntity(),
                confidence=0.0,
                raw_text=user_input.text,
                confidence_level=ConfidenceLevel.VERY_LOW
            ),
            learning_data={},
            session_data={"error": True}
        )

    def _collect_learning_data(
            self,
            user_input: UserInput,
            extracted_info: ExtractedInfo,
            response: ChatbotResponse,
            preprocessed: Any
    ) -> Dict[str, Any]:
        """학습 데이터 수집"""
        learning_data = {
            "timestamp": user_input.timestamp.isoformat(),
            "user_id": user_input.user_id,
            "input_text": user_input.text,
            "extracted_intent": extracted_info.intent.value,
            "extracted_entities": asdict(extracted_info.entities) if extracted_info.entities else {},
            "confidence": extracted_info.confidence,
            "response_text": response.text,
            "emotion": preprocessed.emotion.value if preprocessed else "neutral",
            "keywords": preprocessed.extracted_keywords if preprocessed else [],
            "user_strategy": self._determine_user_strategy(user_input.user_id),
            "conversation_turn": len(self.conversation_memory.get_recent_conversations(user_input.user_id)),
            "session_id": user_input.session_id
        }

        # Feature 추출
        if extracted_info.entities:
            entities = extracted_info.entities

            # 음식 선호도
            if entities.food_type:
                learning_data["food_preference_extracted"] = entities.food_type

            # 예산 패턴
            if entities.budget:
                learning_data["budget_pattern_extracted"] = entities.budget

            # 동반자 패턴
            if entities.companions:
                learning_data["companion_pattern_extracted"] = entities.companions

            # 위치 선호도
            if entities.location_preference:
                learning_data["location_preference_extracted"] = entities.location_preference

        # 추천 관련 데이터
        if response.recommendations:
            learning_data["recommendation_provided"] = True
            learning_data["recommendation_count"] = len(response.recommendations)
            learning_data["recommendations"] = response.recommendations
        else:
            learning_data["recommendation_provided"] = False

        return learning_data

    def _determine_user_strategy(self, user_id: str) -> str:
        """사용자 전략 결정 (간단 버전)"""
        if self.user_manager:
            return self.user_manager.determine_user_strategy(user_id)
        return "normal_mode"

    def _generate_session_data(
            self,
            user_input: UserInput,
            extracted_info: ExtractedInfo,
            response: ChatbotResponse
    ) -> Dict[str, Any]:
        """세션 데이터 생성"""
        return {
            "session_id": user_input.session_id,
            "conversation_turn": len(self.conversation_memory.get_recent_conversations(user_input.user_id)) + 1,
            "intent_confidence": extracted_info.confidence,
            "response_length": len(response.text),
            "has_recommendations": len(response.recommendations) > 0,
            "has_follow_ups": len(response.follow_up_questions) > 0,
            "processing_timestamp": datetime.now().isoformat()
        }

    def _periodic_cleanup(self):
        """주기적 메모리 정리"""
        current_time = datetime.now()

        # 1시간마다 정리
        if current_time - self.last_cleanup_time > timedelta(hours=1):
            logger.info("주기적 메모리 정리 실행...")

            # 모델 메모리 정리
            if self.model:
                self.model.cleanup_memory()

            # 오래된 대화 기록 정리 (24시간 이상)
            self._cleanup_old_conversations()

            self.last_cleanup_time = current_time
            logger.info("메모리 정리 완료")

    def _cleanup_old_conversations(self):
        """오래된 대화 기록 정리"""
        cutoff_time = datetime.now() - timedelta(hours=24)

        for user_id in list(self.conversation_memory.conversations.keys()):
            conversations = self.conversation_memory.conversations[user_id]
            recent_conversations = []

            for conv in conversations:
                conv_time = datetime.fromisoformat(conv["timestamp"])
                if conv_time > cutoff_time:
                    recent_conversations.append(conv)

            if recent_conversations:
                self.conversation_memory.conversations[user_id] = recent_conversations
            else:
                del self.conversation_memory.conversations[user_id]

    def chat(self, message: str, user_id: str = "default_user") -> str:
        """간단한 채팅 인터페이스"""
        user_input = UserInput(
            text=message,
            user_id=user_id,
            timestamp=datetime.now()
        )

        output = self.process_user_input(user_input)
        return output.response.text

    def get_conversation_history(self, user_id: str, count: int = 10) -> List[Dict]:
        """대화 기록 조회"""
        return self.conversation_memory.get_recent_conversations(user_id, count)

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """사용자 프로필 조회"""
        if not self.user_manager:
            return None
        return self.user_manager.get_user_profile(user_id)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 지표 조회"""
        metrics = self.performance_monitor.get_performance_summary()

        # 추가 시스템 정보
        if self.model:
            model_info = self.model.get_model_info()
            metrics.update(model_info)

        metrics["knowledge_base_size"] = {
            "shops": len(self.knowledge.shops) if self.knowledge else 0,
            "menus": len(self.knowledge.menus) if self.knowledge else 0,
            "coupons": len(self.knowledge.coupons) if self.knowledge else 0
        }

        return metrics

    def reset_conversation(self, user_id: str = None):
        """대화 리셋"""
        if user_id:
            self.conversation_memory.clear_conversations(user_id)
            if self.nlu:
                self.nlu.clear_context(user_id)
            logger.info(f"사용자 {user_id} 대화 리셋")
        else:
            self.conversation_memory.clear_conversations()
            if self.nlu:
                self.nlu.clear_context()
            logger.info("모든 대화 리셋")

    def save_state(self, file_path: str):
        """챗봇 상태 저장"""
        state = {
            "conversation_memory": self.conversation_memory.conversations,
            "performance_metrics": self.performance_monitor.metrics,
            "timestamp": datetime.now().isoformat()
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        logger.info(f"챗봇 상태 저장: {file_path}")

    def load_state(self, file_path: str):
        """챗봇 상태 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            self.conversation_memory.conversations = state.get("conversation_memory", {})
            self.performance_monitor.metrics.update(state.get("performance_metrics", {}))

            logger.info(f"챗봇 상태 로드: {file_path}")

        except Exception as e:
            logger.warning(f"챗봇 상태 로드 실패: {e}")

    def __del__(self):
        """소멸자"""
        try:
            if self.model:
                self.model.cleanup_memory()
        except:
            pass

    def _smart_nlu_processing(self, user_input: UserInput, preprocessed) -> ExtractedInfo:
        """스마트 NLU 처리 (LLM 통합)"""

        # LLM 정규화 사용 여부 결정
        if (self.llm_normalizer and
                self.llm_normalizer.should_use_llm_normalization(user_input.text)):

            logger.debug(f"복잡한 입력 감지, LLM 정규화 사용: {user_input.text}")

            # 대화 맥락 수집
            conversation_context = self.conversation_memory.get_recent_conversations(
                user_input.user_id, 3
            )

            # 사용자 맥락 수집
            user_profile = self.user_manager.get_user_profile(user_input.user_id)
            user_context = {}
            if user_profile:
                user_context = {
                    "preferred_foods": user_profile.preferred_categories,
                    "usual_budget": user_profile.average_budget
                }

            # LLM으로 입력 정규화
            llm_output = self.llm_normalizer.normalize_user_input(
                user_input.text,
                conversation_context,
                user_context
            )

            # LLM 정규화 결과로 NLU 수행
            extracted_info = self.nlu.extract_from_llm_normalized(
                user_input.text, llm_output, user_input.user_id
            )

            logger.debug(f"LLM+NLU 결과: intent={extracted_info.intent.value}, confidence={extracted_info.confidence}")

        else:
            # 기존 방식으로 NLU 수행
            extracted_info = self.nlu.extract_intent_and_entities(
                user_input.text, user_input.user_id
            )
            logger.debug(f"기존 NLU 결과: intent={extracted_info.intent.value}, confidence={extracted_info.confidence}")

        return extracted_info

    def _perform_rag_search(self, user_input: UserInput, extracted_info: ExtractedInfo) -> str:
        """RAG 검색 수행"""
        if not self.retriever:
            return ""
        
        # 추천 관련 의도에서만 RAG 검색 수행
        recommendation_intents = [
            IntentType.FOOD_REQUEST,  # 음식 추천 요청
            IntentType.LOCATION_INQUIRY,  # 가게 위치 문의
            IntentType.MENU_OPTION  # 메뉴 관련 문의
        ]
        
        if extracted_info.intent not in recommendation_intents:
            return ""
        
        try:
            # RAG 검색 수행
            rag_context = self.retriever.get_context_for_llm(user_input.text)
            logger.info(f"RAG 검색 완료: {len(rag_context)} 문자")
            return rag_context
            
        except Exception as e:
            logger.error(f"RAG 검색 실패: {e}")
            return ""

    def _smart_response_generation(
            self,
            extracted_info: ExtractedInfo,
            user_profile,
            user_id: str,
            rag_context: str = ""
    ) -> ChatbotResponse:
        """스마트 응답 생성 (LLM 통합)"""

        # 대화 맥락 수집
        conversation_context = self.conversation_memory.get_recent_conversations(user_id, 3)

        user_strategy = self.user_manager.determine_user_strategy(user_id)

        # 온보딩 모드면 무조건 기존 방식 사용
        if user_strategy == "onboarding_mode":
            logger.debug("온보딩 모드: 템플릿 응답 사용")
            return self.response_generator.generate_response(
                extracted_info=extracted_info,
                user_profile=user_profile,
                conversation_context=conversation_context,
                rag_context=rag_context
            )

        # 창의적 LLM 응답이 필요한지 판단
        if (self.llm_normalizer and
                self.llm_normalizer.should_use_llm_response(extracted_info, conversation_context)):

            logger.debug("창의적 LLM 응답 생성 시도")

            # 먼저 기본 추천 데이터 생성
            base_response = self.response_generator.generate_response(
                extracted_info=extracted_info,
                user_profile=user_profile,
                conversation_context=conversation_context,
                rag_context=rag_context
            )

            # LLM으로 아동 친화적 응답 생성
            llm_response_text = self.llm_normalizer.generate_child_friendly_response(
                extracted_info, base_response.recommendations, conversation_context
            )

            # LLM 응답이 성공적이면 사용
            if llm_response_text and len(llm_response_text.strip()) > 10:
                logger.debug("LLM 응답 생성 성공")
                base_response.text = llm_response_text
                base_response.metadata["generation_method"] = "llm_child_friendly"
            else:
                logger.debug("LLM 응답 생성 실패, 템플릿 사용")
                base_response.metadata["generation_method"] = "template_fallback"

            return base_response

        else:
            # 기존 방식으로 응답 생성
            logger.debug("기존 템플릿 응답 생성")
            response = self.response_generator.generate_response(
                extracted_info=extracted_info,
                user_profile=user_profile,
                conversation_context=conversation_context,
                rag_context=rag_context
            )
            response.metadata["generation_method"] = "template"
            return response


# 편의 함수들
def create_naviyam_chatbot(config) -> NaviyamChatbot:
    """나비얌 챗봇 생성 (편의 함수)"""
    return NaviyamChatbot(config)


def quick_chat(message: str, config, user_id: str = "test_user") -> str:
    """빠른 채팅 (편의 함수)"""
    chatbot = NaviyamChatbot(config)
    return chatbot.chat(message, user_id)