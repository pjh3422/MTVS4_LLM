# backend/storage/sqlite_storage.py
import sqlite3
import json
import datetime
from typing import List, Optional
from models.card import MemorizationCard
from models.review import ReviewRecord

class SQLiteCardStorage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_table()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                card_id TEXT PRIMARY KEY,
                concept TEXT NOT NULL,
                answer TEXT NOT NULL,
                card_type TEXT NOT NULL,
                stage INTEGER NOT NULL,
                next_review TEXT,
                review_history TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_card(self, card: MemorizationCard):
        conn = self._get_conn()
        cursor = conn.cursor()

        history_list = [
            {
                "stage": rec.stage,
                "user_answer": rec.user_answer,
                "is_correct": bool(rec.is_correct),
                "feedback": rec.feedback,
                "timestamp": rec.timestamp.isoformat()
            }
            for rec in card.review_history
        ]
        history_json = json.dumps(history_list)

        next_review_iso = card.next_review.isoformat() if card.next_review else None

        cursor.execute("""
            INSERT OR REPLACE INTO cards
            (card_id, concept, answer, card_type, stage, next_review, review_history)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            card.card_id,
            card.concept,
            card.answer,
            card.card_type,
            card.stage,
            next_review_iso,
            history_json
        ))
        conn.commit()
        conn.close()

    def update_card(self, card: MemorizationCard):
        self.save_card(card)

    def delete_card(self, card_id: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cards WHERE card_id = ?", (card_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def load_card(self, row) -> MemorizationCard:
        card = MemorizationCard(
            concept=row[1],
            answer=row[2],
            card_type=row[3]
        )
        card.card_id = row[0]
        card.stage = int(row[4])
        card.next_review = datetime.datetime.fromisoformat(row[5]) if row[5] else None

        history_list = json.loads(row[6]) if row[6] else []
        card.review_history = [
            ReviewRecord(
                stage=entry["stage"],
                user_answer=entry["user_answer"],
                is_correct=entry["is_correct"],
                feedback=entry["feedback"],
                timestamp=datetime.datetime.fromisoformat(entry["timestamp"])
            )
            for entry in history_list
        ]
        return card

    def get_all_cards(self) -> List[MemorizationCard]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cards")
        rows = cursor.fetchall()
        conn.close()
        return [self.load_card(row) for row in rows]

    def get_due_cards(self) -> List[MemorizationCard]:
        now_iso = datetime.datetime.now().isoformat()
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM cards WHERE next_review <= ?",
            (now_iso,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [self.load_card(row) for row in rows]

    def get_card(self, card_id: str) -> Optional[MemorizationCard]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self.load_card(row)
        return None
