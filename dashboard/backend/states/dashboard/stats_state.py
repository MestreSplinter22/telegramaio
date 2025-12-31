"""Statistics state for dashboard KPIs and charts."""

import reflex as rx
from datetime import datetime
from typing import List
from ..models import BotMetrics


class StatsState(rx.State):
    """Statistics state for handling dashboard KPIs and charts."""
    
    # Dashboard metrics
    total_revenue: float = 0.0
    total_profit: float = 0.0
    total_users: int = 0
    total_transactions: int = 0
    total_gift_cards_sold: int = 0
    
    # Bot metrics
    bot_metrics: List[BotMetrics] = []
    
    # Loading states
    stats_loading: bool = False
    
    # Date filters
    date_range: str = "today"
    custom_start_date: str = ""
    custom_end_date: str = ""
    
    async def load_stats_data(self):
        """Load statistics data."""
        self.stats_loading = True
        yield
        
        # Load sample data - replace with actual API calls
        self.total_revenue = 1250.75
        self.total_profit = 187.50
        self.total_users = 45
        self.total_transactions = 128
        self.total_gift_cards_sold = 89
        
        # Sample bot metrics
        self.bot_metrics = [
            BotMetrics(
                id="metrics_1",
                date=datetime.now(),
                active_users=12,
                total_messages=156,
                commands_executed=89,
                response_time_avg=1.2,
                uptime_percentage=99.8,
                errors_count=2
            )
        ]
        
        self.stats_loading = False
    
    def refresh_stats(self):
        """Refresh statistics data."""
        return self.load_stats_data()
    
    @rx.var
    def daily_revenue(self) -> float:
        """Get daily revenue."""
        return self.total_revenue / 30  # Simplified calculation
    
    @rx.var
    def daily_profit(self) -> float:
        """Get daily profit."""
        return self.total_profit / 30  # Simplified calculation
    
    @rx.var
    def conversion_rate(self) -> float:
        """Get conversion rate (transactions/users)."""
        if self.total_users > 0:
            return (self.total_transactions / self.total_users) * 100
        return 0.0
    
    @rx.var
    def average_order_value(self) -> float:
        """Get average order value."""
        if self.total_transactions > 0:
            return self.total_revenue / self.total_transactions
        return 0.0