"""콘솔 기반 UI 구현"""
from interfaces.ui_interface import IUIService
from services.card_service import CardService
from services.review_service import ReviewService
from services.llm_service import LLMService

class ConsoleUI(IUIService):
    """콘솔 UI - 사용자 입력/출력 처리"""
    
    def __init__(self, card_service: CardService, review_service: ReviewService, llm_service: LLMService):
        self.card_service = card_service
        self.review_service = review_service
        self.llm_service = llm_service
        self.review_service.llm_service = llm_service

    def show_welcome_message(self) -> None:
        print("==== 암기 시스템에 오신 것을 환영합니다! ====")

    def prompt_main_menu(self) -> str:
        print("\n메뉴를 선택하세요:")
        print("1. 새 카드 생성")
        print("2. 복습 진행")
        print("3. 통계 조회")
        print("4. 종료")
        return input("선택: ").strip()

    def handle_create_card(self) -> None:
        concept = input("개념을 입력하세요: ").strip()
        answer = input("정답을 입력하세요: ").strip()
        card_type = input("카드 유형(word/concept): ").strip() or "word"
        card = self.card_service.create_card(concept, answer, card_type)
        print(f"카드가 생성되었습니다. 카드 ID: {card.card_id}")

    def handle_review(self) -> None:
        due_cards = self.card_service.get_due_cards()
        if not due_cards:
            print("복습할 카드가 없습니다.")
            return
        for card in due_cards:
            print(f"\n개념: {card.concept}")
            user_answer = input("답안을 입력하세요: ").strip()
            result = self.review_service.conduct_review(card.card_id, user_answer)
            print(f"피드백: {result['feedback']}")
            if result.get("advanced"):
                print("단계가 진급되었습니다.")
            print(f"다음 복습 예정 시간: {result['next_review']}")

    def handle_view_stats(self) -> None:
        stats = self.card_service.get_stats()
        print("\n=== 통계 ===")
        print(f"총 카드 수: {stats['total']}")
        print(f"단계별 카드 수: {stats['by_stage']}")
        print(f"평균 성공률: {stats['average_success_rate']:.2f}%")
        print(f"복습 예정 카드 수: {stats['due_count']}")

    def show_message(self, message: str) -> None:
        print(message)

    def confirm_action(self, prompt: str) -> bool:
        choice = input(f"{prompt} (y/n): ").strip().lower()
        return choice == "y"
