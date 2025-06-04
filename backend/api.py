# backend/api.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import datetime
from pydantic import BaseModel
from storage.sqlite_storage import SQLiteCardStorage
from services.card_service import CardService
from services.review_service import ReviewService
from services.schedule_service import ScheduleService
from services.llm_service import LLMService
from models.card import MemorizationCard
from config.settings import SystemConfig

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

config = SystemConfig.default()
storage = SQLiteCardStorage(db_path="cards.db")
card_service = CardService(storage)
schedule_service = ScheduleService()
llm_service = LLMService()
review_service = ReviewService(
    llm_service,
    card_service,
    schedule_service,
    config.review
)

class CardIn(BaseModel):
    concept: str
    answer: str
    card_type: str = "word"

class CardOut(BaseModel):
    card_id: str
    concept: str
    answer: str
    card_type: str
    stage: int
    next_review: datetime.datetime = None
    success_rate: float

class DueCardOut(BaseModel):
    card_id: str
    concept: str
    stage: int
    next_review: datetime.datetime = None
    hint: str

class ReviewResponse(BaseModel):
    is_correct: bool
    feedback: str
    next_review: Optional[datetime.datetime] = None
    advanced: Optional[bool] = False
    stage: int
    retry_allowed: bool = False
    completed: bool = False
    related_concepts: Optional[List[str]] = None
    advanced_questions: Optional[List[str]] = None

class ReviewIn(BaseModel):
    user_answer: str

@app.post("/cards", response_model=CardOut)
def create_card(card: CardIn):
    if not card.answer and card.card_type == "concept":
        generated_def = llm_service.generate_concept_definition(card.concept)
        card.answer = generated_def
    new_card: MemorizationCard = card_service.create_card(card.concept, card.answer, card.card_type)
    next_time = schedule_service.get_next_review_time(new_card.stage, new_card.card_type)
    new_card.update_next_review(next_time)
    storage.update_card(new_card)
    return CardOut(
        card_id=new_card.card_id,
        concept=new_card.concept,
        answer=new_card.answer,
        card_type=new_card.card_type,
        stage=new_card.stage,
        next_review=new_card.next_review,
        success_rate=new_card.get_success_rate()
    )

@app.get("/cards", response_model=List[CardOut])
def get_cards():
    cards = card_service.get_all_cards()
    return [
        CardOut(
            card_id=c.card_id,
            concept=c.concept,
            answer=c.answer,
            card_type=c.card_type,
            stage=c.stage,
            next_review=c.next_review,
            success_rate=c.get_success_rate()
        )
        for c in cards
    ]

@app.get("/cards/due", response_model=List[DueCardOut])
def get_due_cards(test: bool = Query(False)):
    if test:
        cards = card_service.get_all_cards()
    else:
        cards = card_service.get_due_cards()
    result = []
    for c in cards:
        hint = llm_service.generate_hint(c.concept, c.answer, c.stage)
        result.append(DueCardOut(
            card_id=c.card_id,
            concept=c.concept,
            stage=c.stage,
            next_review=c.next_review,
            hint=hint
        ))
    return result

@app.get("/cards/{card_id}", response_model=CardOut)
def get_card(card_id: str):
    c = card_service.get_card(card_id)
    if not c:
        raise HTTPException(status_code=404, detail="Card not found")
    return CardOut(
        card_id=c.card_id,
        concept=c.concept,
        answer=c.answer,
        card_type=c.card_type,
        stage=c.stage,
        next_review=c.next_review,
        success_rate=c.get_success_rate()
    )

@app.put("/cards/{card_id}", response_model=CardOut)
def update_card(card_id: str, card: CardIn):
    existing = card_service.get_card(card_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Card not found")
    existing.concept = card.concept
    existing.answer = card.answer
    existing.card_type = card.card_type
    next_time = schedule_service.get_next_review_time(existing.stage, existing.card_type)
    existing.update_next_review(next_time)
    storage.update_card(existing)
    return CardOut(
        card_id=existing.card_id,
        concept=existing.concept,
        answer=existing.answer,
        card_type=existing.card_type,
        stage=existing.stage,
        next_review=existing.next_review,
        success_rate=existing.get_success_rate()
    )

@app.delete("/cards/{card_id}")
def delete_card(card_id: str):
    success = storage.delete_card(card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"detail": "Card deleted"}

@app.post("/cards/{card_id}/review", response_model=ReviewResponse)
def review_card(
    card_id: str,
    review: ReviewIn,
    test: bool = Query(False),
    retry: bool = Query(False)
):
    card = card_service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    result = review_service.process_review(card_id, review.user_answer, retry)
    return ReviewResponse(
        is_correct=result["is_correct"],
        feedback=result["feedback"],
        next_review=result.get("next_review"),
        advanced=result.get("advanced", False),
        stage=result["stage"],
        retry_allowed=result.get("retry_allowed", False),
        completed=result.get("completed", False),
        related_concepts=result.get("related_concepts"),
        advanced_questions=result.get("advanced_questions")
    )
