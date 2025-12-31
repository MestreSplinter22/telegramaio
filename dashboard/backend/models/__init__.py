"""Models package for the Telegram gift card bot dashboard."""

import reflex as rx
from .base import BaseSQLModel
from .user import User
from .transaction import Transaction
from .giftcard import GiftCard
from .bot_log import BotLog
from .bot_config import BotConfig
from .daily_statistics import DailyStatistics
from .gateway_config import GatewayConfig
# from .flow import Flow  # Comentado pois não há classe Flow definida


# Helper function to create all tables
def create_all():
    """Create all database tables using Reflex's built-in functionality."""
    # Reflex gerencia isso automaticamente, mas mantemos a função para compatibilidade se necessário
    pass


__all__ = [
    "BaseSQLModel",
    "User",
    "Transaction",
    "GiftCard",
    "BotLog",
    "BotConfig",
    "DailyStatistics",
    "GatewayConfig",
    "create_all",
]