"""Dashboard stats cards component."""

import reflex as rx
from ...backend.states.dashboard import DashboardState
from ...components.ui.card import card


def stat_card(icon: str, title: str, value: rx.Var, subtitle: str, color: str = "blue") -> rx.Component:
    """Individual stat card component."""
    return card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, class_name=f"h-6 w-6 text-{color}-500"),
                rx.spacer(),
                # Removido o ícone fixo de trending-up para limpar a UI, ou poderia ser dinâmico
                rx.icon("trending-up", class_name="h-4 w-4 text-green-500"),
                class_name="w-full",
            ),
            rx.vstack(
                rx.text(value, class_name="text-2xl font-bold text-foreground"),
                rx.text(title, class_name="text-sm text-muted-foreground"),
                rx.text(subtitle, class_name="text-xs text-muted-foreground"),
                class_name="space-y-1 items-start",
            ),
            class_name="space-y-3 items-start",
        ),
        class_name="w-full p-6",
    )


def dashboard_stats() -> rx.Component:
    """Dashboard stats cards grid."""
    return rx.grid(
        stat_card(
            "dollar-sign",
            "Receita Total",
            f"R$ {DashboardState.total_revenue:.2f}",
            "Acumulado total",
            "green"
        ),
        stat_card(
            "users",
            "Usuários",
            DashboardState.total_users.to_string(),
            "Registrados no bot",
            "blue"
        ),
        stat_card(
            "credit-card",
            "Transações",
            DashboardState.total_transactions.to_string(),
            "Total processado",
            "purple"
        ),
        stat_card(
            "gift",
            "Vendas",
            DashboardState.total_gift_cards_sold.to_string(),
            "Produtos entregues",
            "orange"
        ),
        stat_card(
            "wallet",
            "Saldo Usuários",
            f"R$ {DashboardState.total_balance:.2f}",
            "Em carteira",
            "cyan"
        ),
        stat_card(
            "bot",
            "Bot Status",
            DashboardState.bot_uptime,
            f"Resp: {DashboardState.bot_response_time}",
            "teal"
        ),
        class_name="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 w-full",
    )