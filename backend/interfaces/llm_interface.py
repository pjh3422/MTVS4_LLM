# backend/interfaces/llm_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

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
    def generate_hint(self, concept: str, answer: str, stage: int, card_type: str) -> str:
        """
        힌트 생성 (LLM 기반)
        - concept: 카드의 개념 또는 단어
        - answer: 정답 텍스트
        - stage: 현재 복습 단계 (1~4)
        - card_type: "word" 또는 "concept"
        """
        pass

    @abstractmethod
    def generate_feedback(self, card: Dict[str, Any], user_answer: str, is_correct: bool) -> str:
        """피드백 생성 (LLM 기반)"""
        pass

    @abstractmethod
    def generate_related_concepts(self, concept: str, k: int = 5) -> List[str]:
        """주어진 개념과 연관된 개념 리스트 생성"""
        pass

    @abstractmethod
    def generate_concept_definition(self, concept: str) -> str:
        """주어진 개념에 대한 간결한 정의 생성"""
        pass

    @abstractmethod
    def generate_advanced_questions(self, concept: str, n: int = 3) -> List[str]:
        """주어진 개념에 대해 심화 문제(n개) 생성"""
        pass

    @abstractmethod
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """유사도 비교"""
        pass

    @abstractmethod
    def is_equivalent(self, correct_answer: str, user_answer: str) -> bool:
        """yes/no"""
        pass