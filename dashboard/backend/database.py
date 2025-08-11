"""Database configuration and initialization for the Telegram gift card bot."""

import reflex as rx
from .models import User, Transaction, GiftCard, BotLog, BotConfig, DailyStatistics

async def init_database():
    """Initialize the database with sample data if empty."""
    # This will be called when the app starts
    pass

def get_db_session():
    """Get a database session for operations."""
    return rx.session()