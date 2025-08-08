"""Transactions management page for gift card dashboard."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState
from ..templates import template
from ..views.transactions_table import transactions_table



@template(route="/transactions", title="Gestão de Transações")
def transactions() -> rx.Component:
    """Transactions management page.

    Returns:
        The UI for the transactions page.
    """
    return rx.vstack(
        rx.heading("Gestão de Transações", size="5"),
        rx.text("Monitoramento de todas as operações financeiras PIX e compras", size="3", color="gray"),
        
        # Advanced filters
        rx.hstack(
            rx.input(
                rx.input.slot(rx.icon("search"), padding_left="0"),
                placeholder="Buscar transações...",
                size="3",
                width="250px",
                on_change=GiftCardState.set_search_query,
                value=GiftCardState.search_query,
            ),
            rx.select(
                ["all", "deposit", "purchase", "refund", "manual_adjustment"],
                placeholder="Tipo",
                size="3",
                width="150px",
                on_change=GiftCardState.set_transaction_type_filter,
                value=GiftCardState.transaction_type_filter,
            ),
            rx.select(
                ["all", "pending", "completed", "failed", "refunded"],
                placeholder="Status",
                size="3",
                width="150px",
                on_change=GiftCardState.set_status_filter,
                value=GiftCardState.status_filter,
            ),
            rx.select(
                ["1d", "7d", "30d", "90d", "all"],
                placeholder="Período",
                size="3",
                width="120px",
                on_change=GiftCardState.set_date_range,
                value=GiftCardState.date_range,
            ),
            rx.button(
                "Exportar Excel",
                size="3",
                color_scheme="green",
                on_click=rx.download(
                    data="transactions_report",
                    filename="transacoes.xlsx"
                ),
            ),
            spacing="4",
            align="center",
        ),
        
        # Summary cards
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Total de Transações", size="3", color="gray"),
                    rx.text(GiftCardState.total_transactions, size="5", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Receita Total", size="3", color="gray"),
                    rx.text(f"R$ {GiftCardState.total_revenue:.2f}", size="5", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("PIX Processados", size="3", color="gray"),
                    rx.text("247", size="5", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            gap="4",
            grid_template_columns=["repeat(3, 1fr)"],
            width="100%",
        ),
        
        # Transactions table
        transactions_table(),
        
        spacing="6",
        width="100%",
    )