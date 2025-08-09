"""Main overview page for gift card dashboard."""

import reflex as rx
from ..components.ui.card import card
from ..components.notification import notification
from ..backend.giftcard_state import GiftCardState
from ..templates import template
from ..views.overview.dashboard_stats import dashboard_stats
from ..views.overview.revenue_chart import revenue_chart
from ..views.overview.recent_transactions import recent_transactions
from ..views.overview.bot_status import bot_status_card


@template(route="/", title="Overview", on_load=GiftCardState.load_sample_data)
def overview() -> rx.Component:
    """The main overview page for gift card dashboard.

    Returns:
        The UI for the overview page.
    """
    return rx.vstack(
        # Main dashboard stats
        dashboard_stats(),
        
        rx.grid(
            card(revenue_chart(), class_name="w-full"),
            card(bot_status_card(), class_name="w-full"),
            card(recent_transactions(), class_name="w-full"),
            class_name="gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 w-full",
        ),
        
        class_name="space-y-8 w-full",
    )