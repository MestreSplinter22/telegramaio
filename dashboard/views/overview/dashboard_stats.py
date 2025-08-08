"""Dashboard stats cards component."""

import reflex as rx
from ...backend.giftcard_state import GiftCardState
from ...components.card import card


def stat_card(icon: str, title: str, value: str, subtitle: str, color: str = "blue") -> rx.Component:
    """Individual stat card component."""
    return card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, class_name=f"h-6 w-6 text-{color}-500"),
                rx.spacer(),
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
            f"R$ {GiftCardState.total_revenue:.2f}",
            "+12% vs mês anterior",
            "green"
        ),
        stat_card(
            "users",
            "Usuários Totais",
            str(GiftCardState.total_users),
            f"{GiftCardState.active_users} ativos",
            "blue"
        ),
        stat_card(
            "credit-card",
            "PIX Processados",
            str(GiftCardState.total_transactions),
            "Hoje: 47 transações",
            "purple"
        ),
        stat_card(
            "gift",
            "Gift Cards Vendidos",
            str(GiftCardState.total_gift_cards_sold),
            "Este mês: 156 unidades",
            "orange"
        ),
        stat_card(
            "wallet",
            "Saldo Total",
            f"R$ {GiftCardState.total_balance:.2f}",
            "Em carteiras de usuários",
            "cyan"
        ),
        stat_card(
            "bot",
            "Performance Bot",
            "99.8%",
            "Uptime - 2ms resposta",
            "teal"
        ),
        class_name="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 w-full",
    )