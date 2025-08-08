"""Recent transactions component for overview page."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState


def transaction_status_badge(status: str) -> rx.Component:
    """Transaction status badge."""
    color_map = {
        "completed": ("green", "Concluída"),
        "pending": ("yellow", "Pendente"),
        "failed": ("red", "Falhou"),
        "refunded": ("blue", "Reembolsada")
    }
    color, text = color_map.get(status, ("gray", status))
    
    return rx.badge(
        text,
        color_scheme=color,
        variant="surface",
        size="1",
    )


def recent_transactions() -> rx.Component:
    """Recent transactions list."""
    return rx.vstack(
        rx.text("Transações Recentes", size="4", weight="medium"),
        rx.vstack(
            rx.foreach(
                GiftCardState.transactions[:5],  # Show last 5
                lambda transaction: rx.hstack(
                    rx.vstack(
                        rx.text(transaction.description, size="3", weight="medium"),
                        rx.text(f"R$ {transaction.amount:.2f}", size="2", color="gray"),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.spacer(),
                    transaction_status_badge(transaction.status),
                    width="100%",
                    padding="3",
                    border_bottom=f"1px solid {rx.color('gray', 4)}",
                    _last={"border_bottom": "none"},
                )
            ),
            spacing="0",
        ),
        spacing="4",
        width="100%",
    )