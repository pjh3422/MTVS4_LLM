# backend/services/review_service.py

from typing import Dict, Any, List
from interfaces.llm_interface import ILLMService
from services.card_service import CardService
from services.schedule_service import ScheduleService
from models.review import ReviewRecord
from config.settings import ReviewConfig
from datetime import datetime, timedelta

class ReviewService:
    """복습 서비스 - LLM 힌트/피드백 + 4단계 통과 시 관련 개념 추천"""

    def __init__(
        self,
        llm_service: ILLMService,
        card_service: CardService,
        schedule_service: ScheduleService,
        review_config: ReviewConfig | None = None
    ):
        self.llm_service = llm_service
        self.card_service = card_service
        self.schedule_service = schedule_service
        self.review_cfg = review_config or ReviewConfig()

    def process_review(self, card_id: str, user_answer: str, retry: bool = False) -> Dict[str, Any]:
        """
        1) 사용자 답안 평가
        2) 피드백 생성
        3) 만약 stage == 4 & is_correct: related_concepts 반환 (자동 생성은 프론트에서 선택)
           → concept 카드인 경우 심화 문제 생성을 제거했음
        4) is_correct 아닌 경우 기존 재시도/스케줄 로직
        """
        card = self.card_service.get_card(card_id)
        if not card:
            return {"error": "Card not found"}

        # 1) 평가
        is_correct = self.llm_service.evaluate_answer(
            {"concept": card.concept, "answer": card.answer}, user_answer
        )

        # 2) 피드백
        feedback = self.llm_service.generate_feedback(
            {"concept": card.concept, "answer": card.answer},
            user_answer,
            is_correct
        )

        # 리뷰 기록
        record = ReviewRecord(
            stage=card.stage,
            user_answer=user_answer,
            is_correct=is_correct,
            feedback=feedback,
            timestamp=datetime.now()
        )
        card.review_history.append(record)

        result: Dict[str, Any] = {
            "is_correct": is_correct,
            "feedback": feedback,
            "next_review": None,
            "advanced": False,
            "stage": card.stage,
            "retry_allowed": False,
            "completed": False,
            "related_concepts": None,
            "advanced_questions": None
        }

        # 3) 4단계 정답 맞춤: completed 항상 True로 설정
        if is_correct and card.stage == 4:
            result["completed"] = True

            # (심화 문제 생성 제거)
            # if card.card_type == "concept":
            #     adv_qs = self.llm_service.generate_advanced_questions(card.concept)
            #     result["advanced_questions"] = adv_qs

            # 연관 개념 추천
            related = self.llm_service.generate_related_concepts(card.concept)
            result["related_concepts"] = related

            # 단계 진급 및 next_review 설정
            advanced = card.promote_stage()
            next_time = self.schedule_service.get_next_review_time(card.stage, card.card_type)
            card.update_next_review(next_time)
            result["next_review"] = next_time
            result["advanced"] = advanced
            result["stage"] = card.stage

        else:
            # 4단계가 아니거나 틀린 경우: 기존 로직
            if is_correct:
                advanced = card.promote_stage()
                next_time = self.schedule_service.get_next_review_time(card.stage, card.card_type)
                card.update_next_review(next_time)
                result["next_review"] = next_time
                result["advanced"] = advanced
                result["stage"] = card.stage
            else:
                if not retry:
                    result["retry_allowed"] = True
                    result["stage"] = card.stage
                else:
                    card.reset_stage()
                    ten_min_later = datetime.now() + timedelta(minutes=10)
                    card.update_next_review(ten_min_later)
                    result["next_review"] = ten_min_later
                    result["advanced"] = False
                    result["stage"] = card.stage

        self.card_service.update_card(card)
        return result
