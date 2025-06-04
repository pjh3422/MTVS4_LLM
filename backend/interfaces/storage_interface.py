"""저장소 인터페이스 - DIP(의존성 역전 원칙) 준수"""
from abc import ABC, abstractmethod
from typing import List, Optional
from models.card import MemorizationCard

class ICardStorage(ABC):
    """카드 저장소 인터페이스"""
    
    @abstractmethod
    def save_card(self, card: MemorizationCard) -> None:
        """카드 저장"""
        pass
    
    @abstractmethod
    def get_card(self, card_id: str) -> Optional[MemorizationCard]:
        """카드 조회"""
        pass
    
    @abstractmethod
    def get_all_cards(self) -> List[MemorizationCard]:
        """모든 카드 조회"""
        pass
    
    @abstractmethod
    def update_card(self, card: MemorizationCard) -> None:
        """카드 업데이트"""
        pass
    
    @abstractmethod
    def delete_card(self, card_id: str) -> bool:
        """카드 삭제"""
        pass
    
    @abstractmethod
    def get_due_cards(self) -> List[MemorizationCard]:
        """복습 예정 카드 조회"""
        pass
