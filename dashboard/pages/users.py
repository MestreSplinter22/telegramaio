"""Users management page for gift card dashboard."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState, User
from ..templates import template
from ..views.users_table import users_table



@template(route="/users", title="Gestão de Usuários")
def users() -> rx.Component:
    """Users management page.

    Returns:
        The UI for the users page.
    """
    return rx.vstack(
        rx.heading("Gestão de Usuários", size="5"),
        rx.text("Gerencie usuários do bot Telegram e suas carteiras", size="3", color="gray"),
        
        # Filters and search
        rx.hstack(
            rx.input(
                rx.input.slot(rx.icon("search"), padding_left="0"),
                placeholder="Buscar por nome, username ou email...",
                size="3",
                width="300px",
                on_change=GiftCardState.set_search_query,
                value=GiftCardState.search_query,
            ),
            rx.select(
                ["all", "active", "suspended", "banned"],
                placeholder="Status",
                size="3",
                width="150px",
                on_change=GiftCardState.set_status_filter,
                value=GiftCardState.status_filter,
            ),
            rx.button(
                "Exportar CSV",
                size="3",
                color_scheme="blue",
                on_click=rx.download(
                    data="users_data",
                    filename="usuarios_telegram.csv"
                ),
            ),
            spacing="4",
            align="center",
        ),
        
        # Users table
        users_table(),
        
        spacing="6",
        width="100%",
    )