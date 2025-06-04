"""리뷰 기록 모델"""
import datetime
from dataclasses import dataclass

@dataclass
class ReviewRecord:
    """리뷰 기록 모델 - SRP(단일 책임 원칙) 준수"""
    stage: int
    user_answer: str
    is_correct: bool
    feedback: str = ""
    timestamp: datetime.datetime = datetime.datetime.now()
    
    def __str__(self) -> str:
        result = "정답" if self.is_correct else "오답"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] 단계{self.stage}: {result}"

@dataclass
class ReviewQuestion:
    """복습 문제 모델"""
    concept: str
    stage: int
    hint: str = ""
    
    def has_hint(self) -> bool:
        return bool(self.hint.strip())
