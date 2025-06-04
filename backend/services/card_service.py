"""카드 관리 서비스"""
from typing import List, Optional
from interfaces.storage_interface import ICardStorage
from models.card import MemorizationCard
from utils.validators import CardValidator

class CardService:
    """카드 관리 서비스 - SRP, DIP 준수"""
    
    def __init__(self, storage: ICardStorage):
        self.storage = storage
        self.validator = CardValidator()
    
    def create_card(self, concept: str, answer: str, card_type: str = "word") -> MemorizationCard:
        """새 카드 생성"""
        self.validator.validate_concept(concept)
        self.validator.validate_answer(answer)
        self.validator.validate_card_type(card_type)
        
        card = MemorizationCard(concept=concept, answer=answer, card_type=card_type)
        self.storage.save_card(card)
        return card

    def get_card(self, card_id: str) -> Optional[MemorizationCard]:
        """카드 조회"""
        return self.storage.get_card(card_id)

    def get_all_cards(self) -> List[MemorizationCard]:
        """모든 카드 조회"""
        return self.storage.get_all_cards()

    def update_card(self, card: MemorizationCard) -> None:
        """카드 업데이트"""
        self.validator.validate_concept(card.concept)
        self.validator.validate_answer(card.answer)
        self.storage.update_card(card)

    def delete_card(self, card_id: str) -> bool:
        """카드 삭제"""
        return self.storage.delete_card(card_id)

    def get_due_cards(self) -> List[MemorizationCard]:
        """복습 예정 카드 조회"""
        return self.storage.get_due_cards()

    def get_stats(self) -> dict:
        """통계 조회"""
        cards = self.get_all_cards()
        stage_counts = {}
        total_success_rate = 0
        
        for card in cards:
            stage_counts[card.stage] = stage_counts.get(card.stage, 0) + 1
            total_success_rate += card.get_success_rate()
        
        return {
            "total": len(cards),
            "by_stage": stage_counts,
            "average_success_rate": total_success_rate / len(cards) if cards else 0,
            "due_count": len(self.get_due_cards())
        }
