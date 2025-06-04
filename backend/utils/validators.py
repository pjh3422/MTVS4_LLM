"""입력 검증기 모듈"""
import re

class CardValidator:
    """카드 입력 검증"""
    
    def validate_concept(self, concept: str) -> None:
        if not concept or len(concept) < 1:
            raise ValueError("개념은 비어있을 수 없습니다.")
        if len(concept) > 100:
            raise ValueError("개념은 100자 이내여야 합니다.")

    def validate_answer(self, answer: str) -> None:
        if not answer or len(answer) < 1:
            raise ValueError("정답은 비어있을 수 없습니다.")
        if len(answer) > 200:
            raise ValueError("정답은 200자 이내여야 합니다.")

    def validate_card_type(self, card_type: str) -> None:
        if card_type not in ["word", "concept"]:
            raise ValueError("카드 유형은 'word' 또는 'concept'이어야 합니다.")
