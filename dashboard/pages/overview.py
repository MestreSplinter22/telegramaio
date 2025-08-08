"""Main overview page for gift card dashboard."""

import reflex as rx
from ..components.card import card
from ..components.notification import notification
from ..backend.giftcard_state import GiftCardState
from ..templates import template
from ..views.dashboard_stats import dashboard_stats
from ..views.revenue_chart import revenue_chart
from ..views.recent_transactions import recent_transactions
from ..views.bot_status import bot_status_card


@template(route="/", title="Overview", on_load=GiftCardState.load_sample_data)
def overview() -> rx.Component:
    """The main overview page for gift card dashboard.

    Returns:
        The UI for the overview page.
    """
    return rx.vstack(
        rx.heading("Dashboard Telegram Gift Cards", size="6"),
        rx.text("Monitoramento e gestão do sistema de vendas via Telegram", size="4", color="gray"),
        
        # Main dashboard stats
        dashboard_stats(),
        
        rx.grid(
            card(
                rx.hstack(
                    rx.icon("trending-up", size=20),
                    rx.text("Performance Financeira", size="4", weight="medium"),
                    align="center",
                    spacing="2",
                ),
                revenue_chart(),
                width="100%",
            ),
            card(
                rx.hstack(
                    rx.icon("robot", size=20),
                    rx.text("Status do Bot", size="4", weight="medium"),
                    align="center",
                    spacing="2",
                ),
                bot_status_card(),
                width="100%",
            ),
            card(
                rx.hstack(
                    rx.icon("activity", size=20),
                    rx.text("Transações Recentes", size="4", weight="medium"),
                    align="center",
                    spacing="2",
                ),
                recent_transactions(),
                width="100%",
            ),
            gap="1.5rem",
            grid_template_columns=[
                "1fr",
                "repeat(1, 1fr)",
                "repeat(2, 1fr)",
                "repeat(3, 1fr)",
            ],
            width="100%",
        ),
        
        spacing="6",
        width="100%",
    )