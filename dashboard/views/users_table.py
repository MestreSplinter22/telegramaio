"""Users table component for gift card dashboard."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState, User


def user_status_badge(status: str) -> rx.Component:
    """User status badge component."""
    return rx.badge(
        rx.cond(
            status == "active",
            "Ativo",
            rx.cond(
                status == "suspended",
                "Suspenso",
                rx.cond(
                    status == "banned",
                    "Banido",
                    status
                )
            )
        ),
        color_scheme=rx.cond(
            status == "active",
            "green",
            rx.cond(
                status == "suspended",
                "yellow",
                rx.cond(
                    status == "banned",
                    "red",
                    "gray"
                )
            )
        ),
        variant="surface",
        size="2",
    )


def risk_score_badge(score: float) -> rx.Component:
    """Risk score badge component."""
    return rx.badge(
        f"{score:.0f}%",
        color_scheme=rx.cond(
            score < 30,
            "green",
            rx.cond(
                score < 70,
                "yellow",
                "red"
            )
        ),
        variant="surface",
        size="2",
    )


def users_table() -> rx.Component:
    """Users table component."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Usuários", size="4", weight="medium"),
                rx.spacer(),
                rx.text(f"Total: {GiftCardState.users.length()} usuários", size="2", color="gray"),
                width="100%",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Usuário"),
                        rx.table.column_header_cell("Telegram"),
                        rx.table.column_header_cell("Saldo"),
                        rx.table.column_header_cell("Gasto Total"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Risco"),
                        rx.table.column_header_cell("Ações"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        GiftCardState.users,
                        lambda user: rx.table.row(
                            rx.table.cell(
                                rx.vstack(
                                    rx.text(user.name, size="3", weight="medium"),
                                    rx.text(user.email, size="2", color="gray"),
                                    spacing="1",
                                    align_items="start",
                                )
                            ),
                            rx.table.cell(
                                rx.vstack(
                                    rx.text(f"@{user.username}", size="3"),
                                    rx.text(user.telegram_id, size="2", color="gray"),
                                    spacing="1",
                                    align_items="start",
                                )
                            ),
                            rx.table.cell(
                                rx.text(f"R$ {user.balance:.2f}", size="3", weight="medium")
                            ),
                            rx.table.cell(
                                rx.text(f"R$ {user.total_spent:.2f}", size="3")
                            ),
                            rx.table.cell(
                                user_status_badge(user.status)
                            ),
                            rx.table.cell(
                                risk_score_badge(user.risk_score)
                            ),
                            rx.table.cell(
                                rx.hstack(
                                    rx.button(
                                        "Ver Detalhes",
                                        size="2",
                                        variant="ghost",
                                        on_click=GiftCardState.set_selected_user(user),
                                    ),
                                    rx.button(
                                        "Carteira",
                                        size="2",
                                        variant="ghost",
                                        color_scheme="blue",
                                    ),
                                    spacing="2",
                                )
                            ),
                        )
                    )
                ),
                width="100%",
            ),
            spacing="4",
        ),
        padding="6",
        width="100%",
    )