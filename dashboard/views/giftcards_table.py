"""Gift cards table component."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState


def giftcard_status_badge(status: str) -> rx.Component:
    """Gift card status badge."""
    return rx.badge(
        rx.cond(
            status == "available",
            "Disponível",
            rx.cond(
                status == "sold",
                "Vendido",
                rx.cond(
                    status == "expired",
                    "Expirado",
                    rx.cond(
                        status == "pending",
                        "Pendente",
                        status
                    )
                )
            )
        ),
        color_scheme=rx.cond(
            status == "available",
            "green",
            rx.cond(
                status == "sold",
                "blue",
                rx.cond(
                    status == "expired",
                    "red",
                    rx.cond(
                        status == "pending",
                        "yellow",
                        "gray"
                    )
                )
            )
        ),
        variant="surface",
    )


def giftcards_table() -> rx.Component:
    """Gift cards table component."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Produto"),
                rx.table.column_header_cell("Categoria"),
                rx.table.column_header_cell("Preço"),
                rx.table.column_header_cell("Estoque"),
                rx.table.column_header_cell("Vendas"),
                rx.table.column_header_cell("Status"),
                rx.table.column_header_cell("Ações"),
            )
        ),
        rx.table.body(
            rx.foreach(
                GiftCardState.gift_cards,
                lambda giftcard: rx.table.row(
                    rx.table.cell(giftcard.name),
                    rx.table.cell(giftcard.category),
                    rx.table.cell(f"R$ {giftcard.selling_price:.2f}"),
                    rx.table.cell(giftcard.stock),
                    rx.table.cell(giftcard.sold_count),
                    rx.table.cell(giftcard_status_badge(giftcard.status)),
                    rx.table.cell(
                        rx.button(
                            "Editar",
                            size="1",
                        )
                    ),
                )
            )
        ),
        width="100%",
    )