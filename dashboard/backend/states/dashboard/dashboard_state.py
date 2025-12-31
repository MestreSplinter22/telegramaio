"""Main dashboard state coordinating other sub-states."""

import reflex as rx
from ..dashboard.stats_state import StatsState

class DashboardState(rx.State):
    """Main dashboard state coordinating sub-states."""
    
    # Atributos para estatísticas do dashboard
    total_revenue: float = 0.0
    total_users: int = 0
    total_transactions: int = 0
    total_gift_cards_sold: int = 0
    
    def load_dashboard_data(self):
        """Load dashboard data."""
        # Retorna a ação para carregar os dados do stats_state
        return StatsState.load_stats_data
    
    def refresh_dashboard(self):
        """Refresh dashboard data."""
        # Retorna a ação para atualizar os dados do stats_state
        return StatsState.refresh_stats
    
    def sync_stats_to_dashboard(self):
        """Sincroniza dados do stats_state para o dashboard_state."""
        # Obter a instância do StatsState e sincronizar os dados
        stats_state = StatsState()
        self.total_revenue = stats_state.total_revenue
        self.total_users = stats_state.total_users
        self.total_transactions = stats_state.total_transactions
        self.total_gift_cards_sold = stats_state.total_gift_cards_sold