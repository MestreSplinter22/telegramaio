# dashboard/backend/models/giftcard.py

from sqlmodel import Field
from datetime import datetime
from typing import Optional
from .base import BaseSQLModel


class GiftCard(BaseSQLModel, table=True):
    __tablename__ = "giftcard"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    category: str
    value: float
    cost_price: float
    selling_price: float
    status: str = "active"  # active, redeemed, expired
    created_at: datetime = Field(default_factory=datetime.utcnow)
    redeemed_by: Optional[str] = None
    redeemed_at: Optional[datetime] = None