# backend/hook/discord_notifier.py

import json
import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from services.card_service import CardService
from storage.sqlite_storage import SQLiteCardStorage
from services.schedule_service import ScheduleService

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "webhook_config.json")

def load_webhook_url() -> str:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("discord_webhook_url", "")
    return ""

def save_webhook_url(url: str) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"discord_webhook_url": url}, f)

discord_webhook_url = load_webhook_url()

storage = SQLiteCardStorage(db_path="cards.db")
card_service = CardService(storage)
schedule_service = ScheduleService()

def set_webhook_url(url: str):
    global discord_webhook_url
    discord_webhook_url = url
    save_webhook_url(url)

def send_discord_alert(card):
    url = discord_webhook_url
    if not url:
        return
    content = (
        f"🕒 **복습 알림** 🕒\n"
        f"- 카드 ID: `{card.card_id}`\n"
        f"- 개념/단어: **{card.concept}**\n"
        f"- 현재 단계: {card.stage}\n"
        f"- 지금 복습하세요!"
        f"- http://localhost:3000/review"
    )
    payload = {"content": content}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def check_due_and_notify():
    due_cards = card_service.get_due_cards()
    for card in due_cards:
        send_discord_alert(card)

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(check_due_and_notify, "interval", minutes=1, next_run_time=datetime.now())
    scheduler.start()
