"""Modular state management for the dashboard."""

from .models.base import User, Transaction, GiftCard, BotMetrics
from .dashboard.auth_state import AuthState
from .dashboard.stats_state import StatsState
from .dashboard.ui_state import UIState
from .bot.bot_state import BotState
from .users.user_state import UserState
from .transactions.transaction_state import TransactionState
from .giftcards.giftcard_state import GiftCardProductState
from .dashboard.dashboard_state import DashboardState
from .table.table_state import TableState

__all__ = [
    "User",
    "Transaction", 
    "GiftCard",
    "BotMetrics",
    "AuthState",
    "StatsState",
    "UIState",
    "BotState",
    "UserState",
    "TransactionState",
    "GiftCardProductState",
    "DashboardState",
    "TableState",
]