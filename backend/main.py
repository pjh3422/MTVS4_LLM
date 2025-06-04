"""메인 실행 파일"""
import time
from typing import Dict, Any

from config.settings import SystemConfig
from services.llm_service import LLMService
from services.card_service import CardService
from services.review_service import ReviewService
from services.schedule_service import ScheduleService
from storage.memory_storage import MemoryCardStorage
from ui.console_ui import ConsoleUI
from utils.validators import InputValidator

class MemorizationSystemApp:
    """암기 시스템 메인 애플리케이션 - 의존성 주입을 통한 DIP 준수"""
    
    def __init__(self):
        self.storage = MemoryCardStorage()
        self.card_service = CardService(self.storage)
        self.review_service = ReviewService(self.card_service, ScheduleService())
        self.llm_service = LLMService()
        self.ui = ConsoleUI(self.card_service, self.review_service, self.llm_service)
        self.validator = InputValidator()

    def run(self) -> None:
        """애플리케이션 실행"""
        self.ui.show_welcome_message()
        while True:
            choice = self.ui.prompt_main_menu()
            if choice == "1":
                self.ui.handle_create_card()
            elif choice == "2":
                self.ui.handle_review()
            elif choice == "3":
                self.ui.handle_view_stats()
            elif choice == "4":
                self._exit_system()
            else:
                self.ui.show_message("잘못된 선택입니다. 다시 시도해주세요.")

    def _exit_system(self) -> None:
        """시스템 종료"""
        if self.ui.confirm_action("정말 종료하시겠습니까?"):
            self.ui.show_message("🙏 암기 시스템을 이용해주셔서 감사합니다!")
        else:
            return

def main():
    """메인 함수"""
    app = MemorizationSystemApp()
    app.run()

if __name__ == "__main__":
    main()
