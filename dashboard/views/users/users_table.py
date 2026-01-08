"""Users table component for gift card dashboard."""

import reflex as rx
from ...backend.states.users import UserState
from ...components.ui.card import card


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
                "red"
            )
        ),
        variant="surface",
        class_name="text-xs px-2 py-1",
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
    return card(
        rx.vstack(
            rx.hstack(
                rx.text("Usuários", class_name="text-lg font-medium text-foreground"),
                rx.spacer(),
                rx.text(f"Exibindo: {UserState.filtered_users.length()} usuários", class_name="text-sm text-muted-foreground"),
                class_name="w-full",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Nome", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Identificação", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Saldo", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Gasto Total", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Status", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Risco", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Ações", class_name="text-sm font-medium text-foreground"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        UserState.filtered_users,
                        lambda user: rx.table.row(
                            # Coluna Nome (Unindo First Name e Last Name)
                            rx.table.cell(
                                rx.vstack(
                                    rx.text(f"{user.first_name} {user.last_name}", class_name="text-sm font-medium text-foreground"),
                                    # Removido email pois não existe no model atual
                                    class_name="space-y-1 items-start",
                                )
                            ),
                            # Coluna Identificação (Username e Telegram ID)
                            rx.table.cell(
                                rx.vstack(
                                    rx.text(f"@{user.username}", class_name="text-sm text-foreground"),
                                    rx.text(f"ID: {user.telegram_id}", class_name="text-xs text-muted-foreground"),
                                    class_name="space-y-1 items-start",
                                )
                            ),
                            rx.table.cell(
                                rx.text(f"R$ {user.balance:.2f}", class_name="text-sm font-medium text-foreground")
                            ),
                            rx.table.cell(
                                rx.text(f"R$ {user.total_spent:.2f}", class_name="text-sm text-foreground")
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
                                        on_click=lambda: UserState.set_selected_user(user),
                                        class_name="text-xs",
                                    ),
                                    class_name="space-x-2",
                                )
                            ),
                        )
                    )
                ),
                class_name="w-full",
            ),
            class_name="space-y-4",
        ),
        class_name="w-full p-6",
    )