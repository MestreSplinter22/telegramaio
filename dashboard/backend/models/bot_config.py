# dashboard/backend/models/bot_config.py

from sqlmodel import Field
from datetime import datetime
from typing import Optional
from .base import BaseSQLModel


class BotConfig(BaseSQLModel, table=True):
    __tablename__ = "botconfig"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)