"""Dashboard stats cards component."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState


def stat_card(icon: str, title: str, value: str, subtitle: str, color: str = "blue") -> rx.Component:
    """Individual stat card component."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=24, color=rx.color(color, 11)),
                rx.spacer(),
                rx.icon("trending-up", size=16, color=rx.color("green", 9)),
                width="100%",
            ),
            rx.vstack(
                rx.text(value, size="6", weight="bold"),
                rx.text(title, size="3", color="gray"),
                rx.text(subtitle, size="2", color="gray"),
                spacing="1",
                align_items="start",
            ),
            spacing="3",
            align_items="start",
        ),
        padding="6",
        width="100%",
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
        gap="4",
        grid_template_columns=[
            "1fr",
            "repeat(2, 1fr)",
            "repeat(3, 1fr)",
            "repeat(3, 1fr)",
            "repeat(3, 1fr)",
            "repeat(6, 1fr)",
        ],
        width="100%",
    )