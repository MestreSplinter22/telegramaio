# dashboard/backend/models/bot_log.py

from sqlmodel import Field
from datetime import datetime
from typing import Optional
from .base import BaseSQLModel


class BotLog(BaseSQLModel, table=True):
    __tablename__ = "botlog"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    level: str  # info, warning, error, debug
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    extra_data: Optional[str] = None