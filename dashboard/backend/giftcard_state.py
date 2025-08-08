"""Gift card and Telegram bot state management."""

from typing import List, Optional
import reflex as rx
from datetime import datetime, timedelta
import random


class User(rx.Base):
    """User model for gift card system."""
    id: str
    telegram_id: str
    username: str
    name: str
    email: str
    balance: float
    total_spent: float
    total_orders: int
    created_at: datetime
    last_activity: datetime
    status: str  # active, suspended, banned
    risk_score: float  # 0-100 for fraud detection


class Transaction(rx.Base):
    """Transaction model for PIX and gift card purchases."""
    id: str
    user_id: str
    type: str  # deposit, purchase, refund, manual_adjustment
    amount: float
    status: str  # pending, completed, failed, refunded
    description: str
    pix_key: Optional[str] = None
    pix_transaction_id: Optional[str] = None
    gift_card_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: dict = {}


class GiftCard(rx.Base):
    """Gift card product model."""
    id: str
    name: str
    category: str
    value: float
    cost_price: float
    selling_price: float
    profit_margin: float
    stock: int
    sold_count: int
    status: str  # active, inactive, discontinued
    created_at: datetime
    image_url: Optional[str] = None


class BotMetrics(rx.Base):
    """Bot performance metrics."""
    id: str
    date: datetime
    active_users: int
    total_messages: int
    commands_executed: int
    response_time_avg: float
    uptime_percentage: float
    errors_count: int


class GiftCardState(rx.State):
    """Main state for gift card dashboard."""
    
    # Users
    users: List[User] = []
    selected_user: Optional[User] = None
    
    # Transactions
    transactions: List[Transaction] = []
    selected_transaction: Optional[Transaction] = None
    
    # Gift Cards
    gift_cards: List[GiftCard] = []
    selected_gift_card: Optional[GiftCard] = None
    
    # Bot Metrics
    bot_metrics: List[BotMetrics] = []
    
    # Dashboard metrics
    total_revenue: float = 0
    total_users: int = 0
    active_users: int = 0
    total_transactions: int = 0
    total_gift_cards_sold: int = 0
    total_balance: float = 0
    
    # Filters
    date_range: str = "7d"  # 1d, 7d, 30d, 90d
    transaction_type_filter: str = "all"
    status_filter: str = "all"
    search_query: str = ""
    
    # Modal states
    show_add_giftcard_modal: bool = False
    show_user_details_modal: bool = False
    show_transaction_details_modal: bool = False
    
    def load_sample_data(self):
        """Load sample data for development."""
        # Generate sample users
        sample_users = []
        for i in range(1, 51):
            user = User(
                id=f"user_{i}",
                telegram_id=str(100000000 + i),
                username=f"user{i}",
                name=f"User {i}",
                email=f"user{i}@example.com",
                balance=round(random.uniform(0, 1000), 2),
                total_spent=round(random.uniform(50, 5000), 2),
                total_orders=random.randint(1, 50),
                created_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                last_activity=datetime.now() - timedelta(hours=random.randint(1, 168)),
                status=random.choice(["active", "suspended", "banned"]),
                risk_score=random.uniform(0, 100)
            )
            sample_users.append(user)
        self.users = sample_users
        
        # Generate sample transactions
        sample_transactions = []
        for i in range(1, 201):
            user = random.choice(sample_users)
            trans_type = random.choice(["deposit", "purchase", "refund"])
            amount = round(random.uniform(10, 500), 2)
            
            transaction = Transaction(
                id=f"trans_{i}",
                user_id=user.id,
                type=trans_type,
                amount=amount,
                status=random.choice(["completed", "pending", "failed", "refunded"]),
                description=f"{trans_type} transaction #{i}",
                pix_key=f"pix_key_{i}" if trans_type == "deposit" else None,
                created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                updated_at=datetime.now(),
                metadata={"ip": "192.168.1.1", "user_agent": "Telegram Bot"}
            )
            sample_transactions.append(transaction)
        self.transactions = sample_transactions
        
        # Generate sample gift cards
        gift_card_categories = ["Amazon", "Netflix", "Spotify", "Steam", "PlayStation", "Xbox"]
        sample_gift_cards = []
        for i, category in enumerate(gift_card_categories):
            for value in [25, 50, 100, 200]:
                gift_card = GiftCard(
                    id=f"gc_{category.lower()}_{value}",
                    name=f"{category} ${value}",
                    category=category,
                    value=float(value),
                    cost_price=float(value) * 0.85,
                    selling_price=float(value) * 1.15,
                    profit_margin=0.15,
                    stock=random.randint(10, 100),
                    sold_count=random.randint(50, 500),
                    status="active",
                    created_at=datetime.now() - timedelta(days=random.randint(30, 180))
                )
                sample_gift_cards.append(gift_card)
        self.gift_cards = sample_gift_cards
        
        # Generate bot metrics
        sample_metrics = []
        for i in range(30):
            metrics = BotMetrics(
                id=f"metrics_{i}",
                date=datetime.now() - timedelta(days=i),
                active_users=random.randint(100, 500),
                total_messages=random.randint(1000, 5000),
                commands_executed=random.randint(500, 2000),
                response_time_avg=random.uniform(0.5, 3.0),
                uptime_percentage=random.uniform(98.0, 100.0),
                errors_count=random.randint(0, 10)
            )
            sample_metrics.append(metrics)
        self.bot_metrics = sample_metrics
        
        # Calculate dashboard metrics
        self.total_revenue = sum(t.amount for t in sample_transactions if t.type == "purchase")
        self.total_users = len(sample_users)
        self.active_users = len([u for u in sample_users if u.status == "active"])
        self.total_transactions = len(sample_transactions)
        self.total_gift_cards_sold = len([t for t in sample_transactions if t.type == "purchase"])
        self.total_balance = sum(u.balance for u in sample_users)
    
    def get_filtered_transactions(self) -> List[Transaction]:
        """Get transactions based on current filters."""
        filtered = self.transactions
        
        if self.date_range != "all":
            days = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}[self.date_range]
            cutoff = datetime.now() - timedelta(days=days)
            filtered = [t for t in filtered if t.created_at >= cutoff]
        
        if self.transaction_type_filter != "all":
            filtered = [t for t in filtered if t.type == self.transaction_type_filter]
        
        if self.status_filter != "all":
            filtered = [t for t in filtered if t.status == self.status_filter]
        
        if self.search_query:
            query = self.search_query.lower()
            filtered = [t for t in filtered 
                       if query in t.description.lower() or 
                          any(query in str(getattr(t.user, field, "")).lower() 
                              for field in ["username", "name", "email"])]
        
        return filtered
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return next((u for u in self.users if u.id == user_id), None)
    
    @rx.var
    def filtered_transactions(self) -> List[Transaction]:
        """Get filtered transactions based on current filters."""
        filtered = self.transactions
        
        if self.status_filter != "all":
            filtered = [t for t in filtered if t.status == self.status_filter]
        
        if self.transaction_type_filter != "all":
            filtered = [t for t in filtered if t.transaction_type == self.transaction_type_filter]
        
        if self.search_query:
            filtered = [t for t in filtered 
                       if self.search_query.lower() in t.description.lower() 
                       or self.search_query.lower() in t.id.lower()]
        
        return filtered
    
    def get_user_transactions(self, user_id: str) -> List[Transaction]:
        """Get transactions for a specific user."""
        return [t for t in self.transactions if t.user_id == user_id]
    
    # Filter setters
    def set_date_range(self, date_range: str):
        """Set date range filter."""
        self.date_range = date_range
    
    def set_transaction_type_filter(self, transaction_type: str):
        """Set transaction type filter."""
        self.transaction_type_filter = transaction_type
    
    def set_status_filter(self, status: str):
        """Set status filter."""
        self.status_filter = status
    
    def set_search_query(self, search_query: str):
        """Set search query."""
        self.search_query = search_query
    
    def set_selected_user(self, user: User):
        """Set selected user."""
        self.selected_user = user
        self.show_user_details_modal = True
    
    def set_show_add_giftcard_modal(self, show: bool):
        """Set show add gift card modal."""
        self.show_add_giftcard_modal = show
    
    def set_selected_transaction(self, transaction: Transaction):
        """Set selected transaction."""
        self.selected_transaction = transaction
        self.show_transaction_details_modal = True
    
    # Bot management methods
    def restart_bot(self):
        """Restart bot (simulated)."""
        return rx.toast.success("Bot reiniciado com sucesso", position="top-center")
    
    def clear_logs(self):
        """Clear bot logs (simulated)."""
        return rx.toast.success("Logs limpos com sucesso", position="top-center")