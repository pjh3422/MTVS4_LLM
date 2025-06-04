# backend/config/settings.py
import datetime
from dataclasses import dataclass
from typing import Dict

@dataclass
class ScheduleConfig:
    stage_intervals: Dict[int, datetime.timedelta]

    @classmethod
    def default(cls):
        return cls(stage_intervals={
            1: datetime.timedelta(minutes=10),
            2: datetime.timedelta(hours=24),
            3: datetime.timedelta(days=7),
            4: datetime.timedelta(days=30),
        })

@dataclass
class ReviewConfig:
    """재시도 설정"""
    retry_count_immediate: int = 1
    retry_delay_sec: int = 30  # 기본 대기 30초 (변경 가능)

@dataclass
class LLMConfig:
    """LLM 설정"""
    model_name: str = "gemma3:4b-it-qat"
    temperature: float = 0.7
    embedder_name: str = "nlpai-lab/KoE5"
    similarity_threshold: float = 0.75

@dataclass
class SystemConfig:
    """전체 시스템 설정"""
    schedule: ScheduleConfig
    llm: LLMConfig
    review: ReviewConfig

    @classmethod
    def default(cls):
        return cls(
            schedule=ScheduleConfig.default(),
            llm=LLMConfig(),
            review=ReviewConfig()
        )
