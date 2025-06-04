# backend/interfaces/llm_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class ILLMService(ABC):
    """LLM 서비스 인터페이스"""

    @abstractmethod
    def generate_question(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """학습용 질문 생성"""
        pass

    @abstractmethod
    def evaluate_answer(self, card: Dict[str, Any], user_answer: str) -> bool:
        """사용자 답안 평가"""
        pass

    @abstractmethod
    def generate_hint(self, card: Dict[str, Any]) -> str:
        """힌트 생성 (LLM 기반)"""
        pass

    @abstractmethod
    def generate_feedback(self, card: Dict[str, Any], user_answer: str, is_correct: bool) -> str:
        """피드백 생성 (LLM 기반)"""
        pass
