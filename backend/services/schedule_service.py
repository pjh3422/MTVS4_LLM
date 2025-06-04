"""스케줄 관리 서비스"""
from datetime import datetime, timedelta
from config.settings import SystemConfig

class ScheduleService:
    """스케줄 서비스 - 다음 복습 시간 계산"""
    
    def __init__(self):
        config = SystemConfig.default()
        self.stage_intervals = config.schedule.stage_intervals

    def get_next_review_time(self, stage: int, card_type: str) -> datetime:
        """다음 복습 시간 계산"""
        interval: timedelta = self.stage_intervals.get(stage, timedelta(days=1))
        return datetime.now() + interval
