"""메모리 기반 저장소 구현"""
from typing import Dict, List, Optional
from interfaces.storage_interface import ICardStorage
from models.card import MemorizationCard

class MemoryCardStorage(ICardStorage):
    """메모리 기반 카드 저장소 - LSP, ISP 준수"""
    
    def __init__(self):
        self._cards: Dict[str, MemorizationCard] = {}
    
    def save_card(self, card: MemorizationCard) -> None:
        """카드 저장"""
        self._cards[card.card_id] = card
    
    def get_card(self, card_id: str) -> Optional[MemorizationCard]:
        """카드 조회"""
        return self._cards.get(card_id)
    
    def get_all_cards(self) -> List[MemorizationCard]:
        """모든 카드 조회"""
        return list(self._cards.values())
    
    def update_card(self, card: MemorizationCard) -> None:
        """카드 업데이트"""
        if card.card_id in self._cards:
            self._cards[card.card_id] = card
    
    def delete_card(self, card_id: str) -> bool:
        """카드 삭제"""
        if card_id in self._cards:
            del self._cards[card_id]
            return True
        return False
    
    def get_due_cards(self) -> List[MemorizationCard]:
        """복습 예정 카드 조회"""
        return [card for card in self._cards.values() if card.is_due_for_review()]
        
    def get_cards_count(self) -> int:
        """카드 개수 조회"""
        return len(self._cards)
