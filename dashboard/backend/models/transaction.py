# dashboard/backend/models/transaction.py

from sqlmodel import Field
from datetime import datetime
from typing import Optional
from .base import BaseSQLModel


class Transaction(BaseSQLModel, table=True):
    __tablename__ = "transaction"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    type: str  # deposit, purchase, refund, manual_adjustment
    amount: float
    description: str
    status: str = "pending"  # completed, pending, failed, refunded
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    pix_key: Optional[str] = None
    extra_data: Optional[str] = None