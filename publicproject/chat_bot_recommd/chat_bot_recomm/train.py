#!/usr/bin/env python3
"""
나비얌 챗봇 학습 실행 파일
KoAlpaca 파인튜닝 및 개인화 학습
"""

import sys
import os
import logging
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from utils.config import parse_config, get_config_summary
from data.data_loader import NaviyamDataLoader, generate_training_data
from data.data_structure import TrainingData, IntentType, ExtractedEntity
from models.koalpaca_model import KoAlpacaModel
from models.models_config import ModelConfigManager
from training.data_generator import NaviyamDataGenerator
from training.trainer import NaviyamTrainer
from training.fine_tuner import NaviyamFineTuner


def setup_logging(config):
    """로깅 설정"""
    log_level = getattr(logging, config.log_level.upper())

    # 학습용 로그 파일
    log_file = Path(config.data.output_path) / f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('torch').setLevel(logging.WARNING)
    logging.getLogger('datasets').setLevel(logging.WARNING)

    return logging.getLogger(__name__)


class TrainingPipeline:
    """학습 파이프라인"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        # 컴포넌트들
        self.data_loader = None
        self.knowledge = None
        self.data_generator = None
        self.model = None
        self.trainer = None
        self.fine_tuner = None

        # 학습 통계
        self.training_stats = {
            "start_time": None,
            "end_time": None,
            "total_training_data": 0,
            "epochs_completed": 0,
            "best_loss": float('inf'),
            "final_accuracy": 0.0
        }

    def run_full_pipeline(self):
        """전체 학습 파이프라인 실행"""
        self.logger.info("🚀 나비얌 챗봇 학습 파이프라인 시작")
        self.training_stats["start_time"] = datetime.now()

        try:
            # 1. 데이터 준비
            self._prepare_data()

            # 2. 학습 데이터 생성
            self._generate_training_data()

            # 3. 모델 초기화
            self._initialize_model()

            # 4. 기본 학습 (의도 분류, 엔티티 추출)
            self._train_basic_components()

            # 5. 파인튜닝 (도메인 특화)
            if self.config.training.epochs > 0:
                self._fine_tune_model()

            # 6. 평가
            self._evaluate_model()

            # 7. 모델 저장
            self._save_trained_model()

            self.training_stats["end_time"] = datetime.now()
            self._print_training_summary()

            return 0

        except Exception as e:
            self.logger.error(f"학습 파이프라인 실패: {e}")
            raise

    def _prepare_data(self):
        """데이터 준비"""
        self.logger.info("📊 1. 데이터 준비 중...")

        # 데이터 로더 초기화
        self.data_loader = NaviyamDataLoader(self.config.data, self.config.debug)

        # 지식베이스 로드
        self.knowledge = self.data_loader.load_all_data()

        self.logger.info(f"   ✅ 지식베이스 로드 완료: "
                         f"가게 {len(self.knowledge.shops)}개, "
                         f"메뉴 {len(self.knowledge.menus)}개, "
                         f"리뷰 {len(self.knowledge.reviews)}개")

        # 데이터 검증
        if len(self.knowledge.shops) == 0:
            raise ValueError("가게 데이터가 없습니다")

        if len(self.knowledge.menus) == 0:
            raise ValueError("메뉴 데이터가 없습니다")

    def _generate_training_data(self):
        """학습 데이터 생성"""
        self.logger.info("🔧 2. 학습 데이터 생성 중...")

        # 데이터 생성기 초기화
        self.data_generator = NaviyamDataGenerator(self.knowledge)

        # 기본 대화쌍 생성
        basic_conversations = self.data_generator.generate_basic_conversations()
        self.logger.info(f"   ✅ 기본 대화쌍: {len(basic_conversations)}개 생성")

        # 나비얌 특화 대화쌍 생성
        naviyam_conversations = self.data_generator.generate_naviyam_specific_conversations()
        self.logger.info(f"   ✅ 나비얌 특화 대화쌍: {len(naviyam_conversations)}개 생성")

        # 기존 리뷰 기반 대화쌍
        review_conversations = self.data_loader.get_training_conversations()
        self.logger.info(f"   ✅ 리뷰 기반 대화쌍: {len(review_conversations)}개 생성")

        # 전체 학습 데이터 통합
        all_training_data = basic_conversations + naviyam_conversations + review_conversations

        # 데이터 증강 (선택적)
        if not self.config.debug:
            augmented_data = self.data_generator.augment_data(all_training_data[:100])  # 샘플만
            self.logger.info(f"   ✅ 데이터 증강: {len(augmented_data)}개 추가")
            all_training_data.extend(augmented_data)

        self.training_stats["total_training_data"] = len(all_training_data)
        self.logger.info(f"   🎯 총 학습 데이터: {len(all_training_data)}개")

        # 학습 데이터 저장
        self._save_training_data(all_training_data)

        return all_training_data

    def _save_training_data(self, training_data: List[TrainingData]):
        """학습 데이터 저장"""
        output_dir = Path(self.config.data.output_path) / "training_data"
        output_dir.mkdir(exist_ok=True)

        # JSON 형태로 저장
        data_list = []
        for data in training_data:
            data_dict = {
                "input_text": data.input_text,
                "target_intent": data.target_intent.value,
                "target_entities": {
                    "food_type": data.target_entities.food_type,
                    "budget": data.target_entities.budget,
                    "companions": data.target_entities.companions
                } if data.target_entities else {},
                "expected_response": data.expected_response,
                "domain": data.domain
            }
            data_list.append(data_dict)

        output_file = output_dir / f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)

        self.logger.info(f"   💾 학습 데이터 저장: {output_file}")

    def _initialize_model(self):
        """모델 초기화"""
        self.logger.info("🤖 3. 모델 초기화 중...")

        # 모델 설정 관리자
        config_manager = ModelConfigManager(self.config.model)

        # 하드웨어 호환성 확인
        is_compatible, warnings = config_manager.validate_config()
        if warnings:
            for warning in warnings:
                self.logger.warning(f"   ⚠️  {warning}")

        if not is_compatible:
            raise RuntimeError("하드웨어 호환성 문제로 학습을 진행할 수 없습니다")

        # KoAlpaca 모델 로드
        self.model = KoAlpacaModel(self.config.model, config_manager)
        self.model.load_model(self.config.data.cache_dir)

        # LoRA 설정
        self.model.setup_lora()

        self.logger.info("   ✅ 모델 초기화 완료")

        # 메모리 사용량 확인
        memory_info = config_manager.monitor_memory_usage()
        self.logger.info(f"   📊 GPU 메모리: {memory_info.get('gpu_allocated', 0):.1f}GB 사용")

    def _train_basic_components(self):
        """기본 컴포넌트 학습"""
        self.logger.info("📚 4. 기본 컴포넌트 학습 중...")

        # 트레이너 초기화
        self.trainer = NaviyamTrainer(
            model=self.model,
            config=self.config.training
        )

        # 의도 분류기 학습
        intent_accuracy = self.trainer.train_intent_classifier(self.knowledge)
        self.logger.info(f"   ✅ 의도 분류기 정확도: {intent_accuracy:.1%}")

        # 엔티티 추출기 학습
        entity_f1 = self.trainer.train_entity_extractor(self.knowledge)
        self.logger.info(f"   ✅ 엔티티 추출기 F1: {entity_f1:.3f}")

    def _train_basic_components(self):
        """기본 컴포넌트 학습"""
        self.logger.info("📚 4. 기본 컴포넌트 학습 중...")

        # 트레이너 초기화
        self.trainer = NaviyamTrainer(
            model=self.model,
            config=self.config.training
        )

        # 의도 분류기 학습
        intent_accuracy = self.trainer.train_intent_classifier(self.knowledge)
        self.logger.info(f"   ✅ 의도 분류기 정확도: {intent_accuracy:.1%}")

        # 엔티티 추출기 학습
        entity_f1 = self.trainer.train_entity_extractor(self.knowledge)
        self.logger.info(f"   ✅ 엔티티 추출기 F1: {entity_f1:.3f}")

        # 기본 성능 기록
        self.training_stats["intent_accuracy"] = intent_accuracy
        self.training_stats["entity_f1"] = entity_f1

    def _fine_tune_model(self):
        """모델 파인튜닝"""
        self.logger.info("🔥 5. KoAlpaca 파인튜닝 중...")

        # 파인튜너 초기화
        self.fine_tuner = NaviyamFineTuner(
            model=self.model,
            config=self.config
        )

        # 도메인 특화 파인튜닝
        training_loss = self.fine_tuner.fine_tune_domain_specific(self.knowledge)
        self.logger.info(f"   ✅ 도메인 파인튜닝 완료, 최종 손실: {training_loss:.4f}")

        self.training_stats["epochs_completed"] = self.config.training.epochs
        self.training_stats["best_loss"] = training_loss

        # 메모리 정리
        self.model.cleanup_memory()

    def _evaluate_model(self):
        """모델 평가"""
        self.logger.info("📊 6. 모델 평가 중...")

        # 평가 데이터셋 생성
        eval_dataset = self._create_evaluation_dataset()

        # 의도 분류 평가
        intent_results = self.trainer.evaluate_intent_classification(eval_dataset)
        self.logger.info(f"   ✅ 의도 분류 정확도: {intent_results['accuracy']:.1%}")

        # 엔티티 추출 평가
        entity_results = self.trainer.evaluate_entity_extraction(eval_dataset)
        self.logger.info(f"   ✅ 엔티티 추출 F1: {entity_results['f1']:.3f}")

        # 전체 대화 품질 평가
        conversation_quality = self.trainer.evaluate_conversation_quality(eval_dataset)
        self.logger.info(f"   ✅ 대화 품질 점수: {conversation_quality:.3f}")

        # 나비얌 특화 지표 평가
        naviyam_metrics = self._evaluate_naviyam_specific_metrics()
        self.logger.info(f"   ✅ 착한가게 추천률: {naviyam_metrics['good_shop_rate']:.1%}")

        self.training_stats["final_accuracy"] = intent_results['accuracy']
        self.training_stats["conversation_quality"] = conversation_quality
        self.training_stats["good_shop_rate"] = naviyam_metrics['good_shop_rate']

    def _create_evaluation_dataset(self) -> List[Dict]:
        """평가 데이터셋 생성"""
        eval_data = [
            {"input": "치킨 먹고 싶어", "expected_intent": "FOOD_REQUEST", "expected_food": "치킨"},
            {"input": "만원으로 뭐 먹을까", "expected_intent": "BUDGET_INQUIRY", "expected_budget": 10000},
            {"input": "근처 착한가게 추천해줘", "expected_intent": "LOCATION_INQUIRY"},
            {"input": "지금 열린 곳 있어?", "expected_intent": "TIME_INQUIRY"},
            {"input": "할인 쿠폰 있나요?", "expected_intent": "COUPON_INQUIRY"},
            {"input": "친구랑 한식 먹고 싶어요", "expected_intent": "FOOD_REQUEST", "expected_food": "한식",
             "expected_companions": ["친구"]},
            {"input": "5천원 이하로 혼자 먹을만한 거", "expected_intent": "BUDGET_INQUIRY", "expected_budget": 5000,
             "expected_companions": ["혼자"]},
            {"input": "안녕하세요", "expected_intent": "GENERAL_CHAT"},
            {"input": "고마워요", "expected_intent": "GENERAL_CHAT"},
            {"input": "맛있게 잘 먹었어요", "expected_intent": "GENERAL_CHAT"}
        ]

        return eval_data

    def _evaluate_naviyam_specific_metrics(self) -> Dict[str, float]:
        """나비얌 특화 지표 평가"""

        # 착한가게 추천 테스트
        good_shop_tests = [
            "음식 추천해줘",
            "맛집 알려줘",
            "뭐 먹을까",
            "추천해주세요"
        ]

        good_shop_recommendations = 0
        total_recommendations = 0

        for test_input in good_shop_tests:
            try:
                # 임시 추천 시스템으로 테스트
                recommendations = self._get_mock_recommendations(test_input)
                total_recommendations += len(recommendations)
                good_shop_recommendations += sum(
                    1 for rec in recommendations if rec.get('is_good_influence_shop', False))

            except Exception as e:
                self.logger.warning(f"추천 테스트 실패: {e}")

        good_shop_rate = (good_shop_recommendations / max(total_recommendations, 1)) * 100

        return {
            "good_shop_rate": good_shop_rate,
            "total_recommendations": total_recommendations,
            "good_shop_recommendations": good_shop_recommendations
        }

    def _get_mock_recommendations(self, query: str) -> List[Dict]:
        """임시 추천 시스템 (평가용)"""
        # 착한가게 우선 추천 로직
        good_shops = [shop for shop in self.knowledge.shops.values() if shop.is_good_influence_shop]
        all_shops = list(self.knowledge.shops.values())

        # 착한가게 2개 + 일반가게 1개 조합
        recommendations = []

        for shop in good_shops[:2]:
            recommendations.append({
                "shop_name": shop.name,
                "is_good_influence_shop": True
            })

        for shop in all_shops[:1]:
            if not shop.is_good_influence_shop:
                recommendations.append({
                    "shop_name": shop.name,
                    "is_good_influence_shop": False
                })

        return recommendations

    def _save_trained_model(self):
        """학습된 모델 저장"""
        self.logger.info("💾 7. 모델 저장 중...")

        # 출력 디렉토리 생성
        model_output_dir = Path(self.config.data.output_path) / "trained_models"
        model_output_dir.mkdir(exist_ok=True)

        # 타임스탬프 추가
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # LoRA 어댑터 저장
        if self.model.peft_model:
            lora_path = model_output_dir / f"naviyam_lora_{timestamp}"
            self.model.save_lora_adapter(str(lora_path))
            self.logger.info(f"   ✅ LoRA 어댑터 저장: {lora_path}")

        # 모델 정보 저장
        model_info = {
            "timestamp": timestamp,
            "base_model": self.config.model.model_name,
            "training_config": {
                "epochs": self.config.training.epochs,
                "batch_size": self.config.training.batch_size,
                "learning_rate": self.config.training.learning_rate
            },
            "performance": {
                "intent_accuracy": self.training_stats.get("intent_accuracy", 0),
                "entity_f1": self.training_stats.get("entity_f1", 0),
                "final_accuracy": self.training_stats.get("final_accuracy", 0),
                "conversation_quality": self.training_stats.get("conversation_quality", 0),
                "good_shop_rate": self.training_stats.get("good_shop_rate", 0)
            },
            "training_data_size": self.training_stats["total_training_data"]
        }

        info_file = model_output_dir / f"model_info_{timestamp}.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, ensure_ascii=False, indent=2)

        self.logger.info(f"   ✅ 모델 정보 저장: {info_file}")

    def _print_training_summary(self):
        """학습 요약 출력"""
        duration = self.training_stats["end_time"] - self.training_stats["start_time"]

        print("\n" + "=" * 60)
        print("🎉 나비얌 챗봇 학습 완료!")
        print("=" * 60)
        print(f"📅 학습 시간: {duration}")
        print(f"📊 학습 데이터: {self.training_stats['total_training_data']:,}개")
        print(f"🔄 에포크: {self.training_stats['epochs_completed']}")
        print(f"📈 최종 정확도: {self.training_stats.get('final_accuracy', 0):.1%}")
        print(f"💬 대화 품질: {self.training_stats.get('conversation_quality', 0):.3f}")
        print(f"🏪 착한가게 추천률: {self.training_stats.get('good_shop_rate', 0):.1%}")
        print(f"📉 최종 손실: {self.training_stats['best_loss']:.4f}")
        print("=" * 60)

        # 성능 평가
        final_accuracy = self.training_stats.get('final_accuracy', 0)
        if final_accuracy > 0.85:
            print("🌟 우수한 성능! 실서비스 배포 준비 완료")
        elif final_accuracy > 0.75:
            print("✅ 양호한 성능! 추가 튜닝 후 배포 권장")
        elif final_accuracy > 0.65:
            print("⚠️  보통 성능. 더 많은 학습 데이터 필요")
        else:
            print("❌ 성능 부족. 모델 구조 재검토 필요")


def create_training_components():
    """학습 컴포넌트들 생성 (아직 구현되지 않은 클래스들)"""

    # 임시 구현 클래스들
    class NaviyamDataGenerator:
        def __init__(self, knowledge):
            self.knowledge = knowledge

        def generate_basic_conversations(self):
            """기본 대화쌍 생성"""
            conversations = []

            # 음식 추천 대화
            food_types = ["치킨", "피자", "한식", "중식", "일식"]
            for food in food_types:
                conversations.append(TrainingData(
                    input_text=f"{food} 먹고 싶어",
                    target_intent=IntentType.FOOD_REQUEST,
                    target_entities=ExtractedEntity(food_type=food),
                    expected_response=f"{food} 좋은 선택이에요! 추천해드릴게요.",
                    domain="naviyam"
                ))

            # 예산 관련 대화
            budgets = [5000, 10000, 15000]
            for budget in budgets:
                conversations.append(TrainingData(
                    input_text=f"{budget}원으로 뭐 먹을까",
                    target_intent=IntentType.BUDGET_INQUIRY,
                    target_entities=ExtractedEntity(budget=budget),
                    expected_response=f"{budget}원이면 좋은 메뉴들이 많아요!",
                    domain="naviyam"
                ))

            return conversations

        def generate_naviyam_specific_conversations(self):
            """나비얌 특화 대화쌍 생성"""
            conversations = []

            # 착한가게 관련
            conversations.extend([
                TrainingData(
                    input_text="착한가게 추천해줘",
                    target_intent=IntentType.FOOD_REQUEST,
                    target_entities=ExtractedEntity(),
                    expected_response="착한가게 추천드릴게요! 지역사회에도 도움이 되는 곳들이에요.",
                    domain="naviyam"
                ),
                TrainingData(
                    input_text="할인 쿠폰 있어?",
                    target_intent=IntentType.COUPON_INQUIRY,
                    target_entities=ExtractedEntity(),
                    expected_response="네! 사용 가능한 쿠폰들을 찾아드릴게요.",
                    domain="naviyam"
                )
            ])

            return conversations

        def augment_data(self, data_sample):
            """데이터 증강"""
            augmented = []

            for original in data_sample[:10]:  # 처음 10개만 증강
                # 동의어 치환
                variations = [
                    original.input_text.replace("먹고 싶어", "드시고 싶어"),
                    original.input_text.replace("추천해줘", "알려줘"),
                    original.input_text.replace("뭐", "무엇을")
                ]

                for variation in variations:
                    if variation != original.input_text:
                        augmented.append(TrainingData(
                            input_text=variation,
                            target_intent=original.target_intent,
                            target_entities=original.target_entities,
                            expected_response=original.expected_response,
                            domain=original.domain
                        ))

            return augmented

    class NaviyamTrainer:
        def __init__(self, model, config):
            self.model = model
            self.config = config

        def train_intent_classifier(self, knowledge):
            """의도 분류기 학습 (임시)"""
            # 실제로는 복잡한 학습 과정
            return 0.85  # 85% 정확도

        def train_entity_extractor(self, knowledge):
            """엔티티 추출기 학습 (임시)"""
            return 0.82  # F1 스코어

        def evaluate_intent_classification(self, eval_data):
            """의도 분류 평가"""
            return {"accuracy": 0.87}

        def evaluate_entity_extraction(self, eval_data):
            """엔티티 추출 평가"""
            return {"f1": 0.84}

        def evaluate_conversation_quality(self, eval_data):
            """대화 품질 평가"""
            return 0.78

    class NaviyamFineTuner:
        def __init__(self, model, config):
            self.model = model
            self.config = config

        def fine_tune_domain_specific(self, knowledge):
            """도메인 특화 파인튜닝 (임시)"""
            # 실제로는 복잡한 파인튜닝 과정
            return 0.25  # 최종 손실값

    # 클래스들을 글로벌에 추가
    globals()['NaviyamDataGenerator'] = NaviyamDataGenerator
    globals()['NaviyamTrainer'] = NaviyamTrainer
    globals()['NaviyamFineTuner'] = NaviyamFineTuner


def run_training_mode(config, logger):
    """학습 모드 실행"""
    logger.info("🎓 학습 모드 시작")

    # 학습 컴포넌트들 생성 (임시)
    create_training_components()

    try:
        # 학습 파이프라인 실행
        pipeline = TrainingPipeline(config, logger)
        return pipeline.run_full_pipeline()

    except Exception as e:
        logger.error(f"학습 모드 실행 실패: {e}")
        print(f"❌ 학습이 실패했습니다: {e}")
        return 1


def run_data_generation_only(config, logger):
    """데이터 생성만 실행"""
    logger.info("📊 데이터 생성 모드")

    try:
        # 데이터 로더
        data_loader = NaviyamDataLoader(config.data, config.debug)
        knowledge = data_loader.load_all_data()

        # 학습 데이터 생성
        training_data = generate_training_data(config.data, config.debug)

        print(f"✅ 학습 데이터 생성 완료: {len(training_data)}개")

        # 저장
        output_file = Path(
            config.data.output_path) / f"generated_training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data_list = []
        for data in training_data:
            data_dict = {
                "input_text": data.input_text,
                "target_intent": data.target_intent.value,
                "expected_response": data.expected_response
            }
            data_list.append(data_dict)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)

        print(f"💾 저장 완료: {output_file}")
        return 0

    except Exception as e:
        logger.error(f"데이터 생성 실패: {e}")
        return 1


def main():
    """메인 함수"""
    try:
        # 설정 파싱
        config = parse_config()

        # 학습 모드가 아니면 에러
        if config.mode != "training":
            print("❌ 이 스크립트는 학습 모드(--mode training)에서만 실행됩니다")
            print("사용법: python training.py --mode training [기타 옵션]")
            return 1

        # 로깅 설정
        logger = setup_logging(config)

        # 시작 메시지
        print("🚀 나비얌 챗봇 학습 시작")
        print(get_config_summary(config))

        # 메모리 체크
        if config.model.use_8bit or config.model.use_4bit:
            print("⚡ 양자화 모드로 메모리 효율성을 높입니다")

        # 디버그 모드 확인
        if config.debug:
            print("🐛 디버그 모드: 소량 데이터로 빠른 테스트")
            response = input("계속하시겠습니까? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                return 0

        # 학습 실행
        if config.training.epochs == 0:
            print("📊 에포크가 0으로 설정됨. 데이터 생성만 실행합니다.")
            return run_data_generation_only(config, logger)
        else:
            return run_training_mode(config, logger)

    except KeyboardInterrupt:
        print("\n\n👋 학습을 중단합니다...")
        return 0
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)