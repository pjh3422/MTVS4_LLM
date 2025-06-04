"""암기 카드 모델"""
import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4

from .review import ReviewRecord

@dataclass
class MemorizationCard:
    """암기 카드 모델 - SRP(단일 책임 원칙) 준수"""
    concept: str
    answer: str
    card_type: str = "word"  # 카드 유형: "word" or "concept"
    card_id: str = field(default_factory=lambda: str(uuid4()))
    stage: int = 1
    next_review: datetime.datetime = field(default_factory=lambda: datetime.datetime.now())
    review_history: List[ReviewRecord] = field(default_factory=list)

    def promote_stage(self) -> bool:
        """단계 진급 (4단계 초과시 False 반환)"""
        if self.stage < 4:
            self.stage += 1
            return True
        return False
    
    def reset_stage(self) -> None:
        """1단계로 리셋"""
        self.stage = 1
    
    def update_next_review(self, next_time: datetime.datetime) -> None:
        """다음 복습 시간 업데이트"""
        self.next_review = next_time
    
    def is_due_for_review(self) -> bool:
        """복습 여부 판단"""
        return datetime.datetime.now() >= self.next_review
    
    def get_success_rate(self) -> float:
        """성공률 계산"""
        if not self.review_history:
            return 0.0
        correct_count = sum(1 for record in self.review_history if record.is_correct)
        return correct_count / len(self.review_history) * 100
