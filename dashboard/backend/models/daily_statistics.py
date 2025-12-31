# dashboard/backend/models/daily_statistics.py

from sqlmodel import Field
from datetime import datetime
from typing import Optional
from .base import BaseSQLModel


class DailyStatistics(BaseSQLModel, table=True):
    __tablename__ = "dailystatistics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str  # YYYY-MM-DD format
    total_revenue: float = 0.0
    total_users: int = 0
    active_users: int = 0
    total_transactions: int = 0
    total_gift_cards_sold: int = 0
    total_balance: float = 0.0
    bot_uptime: float = 0.0
    error_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)