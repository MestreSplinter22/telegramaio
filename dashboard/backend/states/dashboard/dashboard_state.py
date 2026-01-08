"""Main dashboard state coordinating other sub-states."""

import reflex as rx
from sqlmodel import select, func
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Importando Models e outros States
from ...models import User, Transaction
from ..transactions.transaction_state import TransactionState

class DashboardState(rx.State):
    """Main dashboard state."""
    
    # KPIs Principais
    total_revenue: float = 0.0
    total_users: int = 0
    total_transactions: int = 0
    total_gift_cards_sold: int = 0
    total_balance: float = 0.0
    
    # Métricas do Bot (Simuladas por enquanto ou calculadas)
    bot_uptime: str = "99.8%"
    bot_response_time: str = "2ms"
    
    # Dados do Gráfico
    revenue_chart_data: List[Dict[str, Any]] = []
    
    async def load_dashboard_data(self):
        """Load all dashboard data from database."""
        
        # CORREÇÃO: Primeiro obtemos a instância do estado com await
        transaction_state = await self.get_state(TransactionState)
        # Depois chamamos o método na instância carregada
        transaction_state.load_transactions()
        
        with rx.session() as session:
            # --- KPI: Receita Total (Soma de transactions completed) ---
            query_rev = select(func.sum(Transaction.amount)).where(Transaction.status == "completed")
            self.total_revenue = session.exec(query_rev).one() or 0.0
            
            # --- KPI: Total de Usuários ---
            query_users = select(func.count(User.id))
            self.total_users = session.exec(query_users).one() or 0
            
            # --- KPI: Total de Transações (Todas) ---
            query_txns = select(func.count(Transaction.id))
            self.total_transactions = session.exec(query_txns).one() or 0
            
            # --- KPI: Gift Cards Vendidos (Purchase + Completed) ---
            query_gifts = select(func.count(Transaction.id)).where(
                Transaction.type == "purchase",
                Transaction.status == "completed"
            )
            self.total_gift_cards_sold = session.exec(query_gifts).one() or 0
            
            # --- KPI: Saldo Total dos Usuários ---
            try:
                query_bal = select(func.sum(User.balance))
                self.total_balance = session.exec(query_bal).one() or 0.0
            except:
                self.total_balance = 0.0

            # --- DADOS DO GRÁFICO (Últimos 7 dias) ---
            self.calculate_revenue_chart(session)
    
    def calculate_revenue_chart(self, session):
        """Calcula a receita dos últimos 7 dias para o gráfico."""
        today = datetime.now().date()
        chart_data = []
        
        # Cria lista dos últimos 7 dias
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        
        for date_obj in dates:
            # Início e fim do dia para filtro
            start_dt = datetime.combine(date_obj, datetime.min.time())
            end_dt = datetime.combine(date_obj, datetime.max.time())
            
            # Query sum amount where status=completed and date in range
            query = select(func.sum(Transaction.amount)).where(
                Transaction.status == "completed",
                Transaction.timestamp >= start_dt,
                Transaction.timestamp <= end_dt
            )
            val = session.exec(query).one() or 0.0
            
            # Formata para o gráfico: "day": "DD/MM", "revenue": Valor
            chart_data.append({
                "day": date_obj.strftime("%d/%m"),
                "revenue": float(val)  # Recharts precisa de float/int
            })
            
        self.revenue_chart_data = chart_data

    def refresh_dashboard(self):
        """Refresh dashboard data."""
        return self.load_dashboard_data