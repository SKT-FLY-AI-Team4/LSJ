"""
나비얌 챗봇 설정 관리
argparse + 기본값 조합으로 유연한 파라미터 관리
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ModelConfig:
    """모델 관련 설정"""
    model_type: str = "ax"  # "koalpaca" or "ax" (A.X 3.1 Lite)
    model_name: str = "skt/A.X-3.1-Light"  # A.X 3.1 Lite 기본값
    use_8bit: bool = False
    use_4bit: bool = True  # A.X 3.1 Lite는 4-bit 양자화 사용
    max_vram_gb: int = 6  # RTX 3060 Ti 기준
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    max_length: int = 512
    temperature: float = 0.7
    do_sample: bool = True
    enable_lora: bool = False  # LoRA 활성화 여부
    lora_path: Optional[str] = None  # LoRA 어댑터 경로


@dataclass
class DataConfig:
    """데이터 관련 설정"""
    data_path: str = "./preprocessed_data"
    output_path: str = "./outputs"
    cache_dir: str = "./cache"
    max_conversations: int = 1000
    save_processed: bool = True


@dataclass
class TrainingConfig:
    """학습 관련 설정"""
    epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 1e-4
    warmup_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 100
    gradient_accumulation_steps: int = 4


@dataclass
class RAGConfig:
    """RAG 시스템 관련 설정"""
    vector_store_type: str = "mock"  # "mock", "faiss", "chromadb", "commercial"
    embedding_model: str = "all-MiniLM-L6-v2"  # SentenceTransformer 모델명
    embedding_dim: int = 384
    index_path: str = "./outputs/faiss_index.faiss"
    top_k: int = 5
    enable_rag: bool = True


@dataclass
class InferenceConfig:
    """추론 관련 설정"""
    max_response_length: int = 200
    confidence_threshold: float = 0.5
    enable_personalization: bool = True
    save_conversations: bool = False
    response_timeout: int = 30  # 초


@dataclass
class AppConfig:
    """전체 앱 설정"""
    mode: str = "chat"  # chat, training, inference, evaluation
    log_level: str = "INFO"
    debug: bool = False
    device: str = "auto"  # auto, cpu, cuda

    # 하위 설정들
    model: ModelConfig = ModelConfig()
    data: DataConfig = DataConfig()
    training: TrainingConfig = TrainingConfig()
    inference: InferenceConfig = InferenceConfig()
    rag: RAGConfig = RAGConfig()


def create_parser() -> argparse.ArgumentParser:
    """명령행 인자 파서 생성"""
    parser = argparse.ArgumentParser(
        description="나비얌 챗봇 - 아동 대상 착한가게 추천 AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # ==============================================
    # 메인 실행 모드
    # ==============================================
    parser.add_argument(
        "--mode",
        choices=["chat", "training", "inference", "evaluation"],
        default="chat",
        help="실행 모드 선택"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="디버그 모드 활성화"
    )

    parser.add_argument(
        "--log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="로그 레벨 설정"
    )

    # ==============================================
    # 데이터 관련
    # ==============================================
    data_group = parser.add_argument_group("데이터 설정")

    data_group.add_argument(
        "--data_path",
        type=str,
        default="./preprocessed_data",
        help="전처리된 데이터 경로"
    )

    data_group.add_argument(
        "--output_path",
        type=str,
        default="./outputs",
        help="출력 파일 저장 경로"
    )

    data_group.add_argument(
        "--cache_dir",
        type=str,
        default="./cache",
        help="캐시 디렉토리 경로"
    )

    data_group.add_argument(
        "--max_conversations",
        type=int,
        default=1000,
        help="최대 대화 기록 수"
    )

    # ==============================================
    # 모델 관련
    # ==============================================
    model_group = parser.add_argument_group("모델 설정")

    model_group.add_argument(
        "--model_type",
        type=str,
        choices=["koalpaca", "ax"],
        default="ax",
        help="모델 타입 선택 (koalpaca: KoAlpaca 5.8B, ax: A.X 3.1 Lite)"
    )

    model_group.add_argument(
        "--model_name", 
        type=str,
        default="skt/A.X-3.1-Light",
        help="사용할 모델 이름"
    )

    model_group.add_argument(
        "--use_8bit",
        action="store_true",
        default=False,
        help="8bit 양자화 사용"
    )

    model_group.add_argument(
        "--use_4bit",
        action="store_true",
        default=True,
        help="4bit 양자화 사용 (A.X 3.1 Lite 기본값)"
    )

    model_group.add_argument(
        "--max_vram_gb",
        type=int,
        default=6,
        help="최대 VRAM 사용량 (GB) - RTX 3060 Ti 기준"
    )

    model_group.add_argument(
        "--lora_rank",
        type=int,
        default=16,
        help="LoRA rank 설정"
    )

    model_group.add_argument(
        "--max_length",
        type=int,
        default=512,
        help="최대 토큰 길이"
    )

    model_group.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="생성 온도 설정"
    )

    # ==============================================
    # 학습 관련
    # ==============================================
    train_group = parser.add_argument_group("학습 설정")

    train_group.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="학습 에포크 수"
    )

    train_group.add_argument(
        "--batch_size",
        type=int,
        default=4,
        help="배치 크기"
    )

    train_group.add_argument(
        "--learning_rate",
        type=float,
        default=1e-4,
        help="학습률"
    )

    train_group.add_argument(
        "--save_steps",
        type=int,
        default=500,
        help="모델 저장 주기"
    )

    # ==============================================
    # 추론 관련
    # ==============================================
    inference_group = parser.add_argument_group("추론 설정")

    inference_group.add_argument(
        "--confidence_threshold",
        type=float,
        default=0.5,
        help="신뢰도 임계값"
    )

    inference_group.add_argument(
        "--enable_personalization",
        action="store_true",
        default=True,
        help="개인화 기능 활성화"
    )

    inference_group.add_argument(
        "--save_conversations",
        action="store_true",
        help="대화 기록 저장"
    )

    inference_group.add_argument(
        "--response_timeout",
        type=int,
        default=30,
        help="응답 타임아웃 (초)"
    )

    return parser


def parse_config() -> AppConfig:
    """명령행 인자를 파싱하여 설정 객체 생성"""
    parser = create_parser()
    args = parser.parse_args()

    # AppConfig 객체 생성
    config = AppConfig()

    # 메인 설정
    config.mode = args.mode
    config.debug = args.debug
    config.log_level = args.log_level

    # 데이터 설정
    config.data.data_path = args.data_path
    config.data.output_path = args.output_path
    config.data.cache_dir = args.cache_dir
    config.data.max_conversations = args.max_conversations

    # 모델 설정
    config.model.model_type = args.model_type
    config.model.model_name = args.model_name
    config.model.use_8bit = args.use_8bit
    config.model.use_4bit = args.use_4bit
    config.model.max_vram_gb = args.max_vram_gb
    config.model.lora_rank = args.lora_rank
    config.model.max_length = args.max_length
    config.model.temperature = args.temperature

    # 학습 설정
    config.training.epochs = args.epochs
    config.training.batch_size = args.batch_size
    config.training.learning_rate = args.learning_rate
    config.training.save_steps = args.save_steps

    # 추론 설정
    config.inference.confidence_threshold = args.confidence_threshold
    config.inference.enable_personalization = args.enable_personalization
    config.inference.save_conversations = args.save_conversations
    config.inference.response_timeout = args.response_timeout

    # 경로 생성
    Path(config.data.output_path).mkdir(exist_ok=True)
    Path(config.data.cache_dir).mkdir(exist_ok=True)

    return config


def get_config_summary(config: AppConfig) -> str:
    """설정 요약 문자열 생성"""
    model_type_display = "A.X 3.1 Lite" if config.model.model_type == "ax" else "KoAlpaca"
    summary = f"""
=== 나비얌 챗봇 설정 ===
모드: {config.mode}
모델 타입: {model_type_display}
모델: {config.model.model_name}
양자화: {'8bit' if config.model.use_8bit else '4bit' if config.model.use_4bit else 'None'}
데이터 경로: {config.data.data_path}
출력 경로: {config.data.output_path}
개인화: {'ON' if config.inference.enable_personalization else 'OFF'}
디버그: {'ON' if config.debug else 'OFF'}
========================
"""
    return summary


# 편의 함수들
def get_default_config() -> AppConfig:
    """기본 설정 반환"""
    return AppConfig()


def save_config(config: AppConfig, path: str):
    """설정을 파일로 저장"""
    import json
    from dataclasses import asdict

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(asdict(config), f, indent=2, ensure_ascii=False)


def load_config(path: str) -> AppConfig:
    """파일에서 설정 로드"""
    import json

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 딕셔너리를 AppConfig로 변환 (간단한 버전)
    config = AppConfig()
    # 실제로는 더 정교한 변환 로직 필요
    return config