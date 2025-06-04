"""UI 서비스 인터페이스 - DIP(의존성 역전 원칙) 준수"""
from abc import ABC, abstractmethod

class IUIService(ABC):
    """UI 서비스 인터페이스"""
    
    @abstractmethod
    def show_welcome_message(self) -> None:
        pass
    
    @abstractmethod
    def prompt_main_menu(self) -> str:
        pass
    
    @abstractmethod
    def handle_create_card(self) -> None:
        pass
    
    @abstractmethod
    def handle_review(self) -> None:
        pass
    
    @abstractmethod
    def handle_view_stats(self) -> None:
        pass
    
    @abstractmethod
    def show_message(self, message: str) -> None:
        pass
    
    @abstractmethod
    def confirm_action(self, prompt: str) -> bool:
        pass
