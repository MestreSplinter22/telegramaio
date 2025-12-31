# dashboard/backend/models/user.py

from sqlmodel import Field
from datetime import datetime
from typing import Optional
from .base import BaseSQLModel


class User(BaseSQLModel, table=True):
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: str
    username: str
    first_name: str
    last_name: str
    balance: float = 0.0
    total_spent: float = 0.0
    status: str = "active"  # active, suspended, banned
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    risk_score: float = 0.0