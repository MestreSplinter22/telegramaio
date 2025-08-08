"""Transactions table component."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState


def transaction_status_badge(status: str) -> rx.Component:
    """Transaction status badge."""
    return rx.badge(
        rx.cond(
            status == "completed",
            "Concluída",
            rx.cond(
                status == "pending",
                "Pendente",
                rx.cond(
                    status == "failed",
                    "Falhou",
                    rx.cond(
                        status == "refunded",
                        "Reembolsada",
                        status
                    )
                )
            )
        ),
        color_scheme=rx.cond(
            status == "completed",
            "green",
            rx.cond(
                status == "pending",
                "yellow",
                rx.cond(
                    status == "failed",
                    "red",
                    rx.cond(
                        status == "refunded",
                        "blue",
                        "gray"
                    )
                )
            )
        ),
        variant="surface",
    )


def transactions_table() -> rx.Component:
    """Transactions table component."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID"),
                rx.table.column_header_cell("Tipo"),
                rx.table.column_header_cell("Valor"),
                rx.table.column_header_cell("Status"),
                rx.table.column_header_cell("Data"),
                rx.table.column_header_cell("Ações"),
            )
        ),
        rx.table.body(
            rx.foreach(
                GiftCardState.filtered_transactions,
                lambda transaction: rx.table.row(
                    rx.table.cell(transaction.id[:8] + "..."),
                    rx.table.cell(transaction.type),
                    rx.table.cell(f"R$ {transaction.amount:.2f}"),
                    rx.table.cell(transaction_status_badge(transaction.status)),
                    rx.table.cell(transaction.created_at),
                    rx.table.cell(
                        rx.button(
                            "Detalhes",
                            size="1",
                            on_click=lambda: GiftCardState.set_selected_transaction(transaction),
                        )
                    ),
                )
            )
        ),
        width="100%",
    )