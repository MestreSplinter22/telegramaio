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
        rx.heading("Gestão de Transações", class_name="text-2xl font-bold text-foreground"),
        rx.text("Monitoramento de todas as operações financeiras PIX e compras", class_name="text-base text-muted-foreground"),
        
        # Advanced filters
        rx.hstack(
            rx.input(
                rx.input.slot(rx.icon("search"), class_name="pl-0"),
                placeholder="Buscar transações...",
                class_name="w-[250px] h-10 px-3 py-2 text-sm rounded-md border border-input bg-background",
                on_change=GiftCardState.set_search_query,
                value=GiftCardState.search_query,
            ),
            rx.select(
                ["all", "deposit", "purchase", "refund", "manual_adjustment"],
                placeholder="Tipo",
                class_name="w-[150px] h-10 px-3 py-2 text-sm rounded-md border border-input bg-background",
                on_change=GiftCardState.set_transaction_type_filter,
                value=GiftCardState.transaction_type_filter,
            ),
            rx.select(
                ["all", "pending", "completed", "failed", "refunded"],
                placeholder="Status",
                class_name="w-[150px] h-10 px-3 py-2 text-sm rounded-md border border-input bg-background",
                on_change=GiftCardState.set_status_filter,
                value=GiftCardState.status_filter,
            ),
            rx.select(
                ["1d", "7d", "30d", "90d", "all"],
                placeholder="Período",
                class_name="w-[120px] h-10 px-3 py-2 text-sm rounded-md border border-input bg-background",
                on_change=GiftCardState.set_date_range,
                value=GiftCardState.date_range,
            ),
            rx.button(
                "Exportar Excel",
                class_name="bg-green-500 text-green-900 hover:bg-green-600 px-4 py-2 rounded-md text-sm font-medium",
                on_click=rx.download(
                    data="transactions_report",
                    filename="transacoes.xlsx"
                ),
            ),
            class_name="items-center space-x-4",
        ),
        
        # Summary cards
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Total de Transações", class_name="text-sm text-muted-foreground"),
                    rx.text(GiftCardState.total_transactions, class_name="text-xl font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Receita Total", class_name="text-sm text-muted-foreground"),
                    rx.text(f"R$ {GiftCardState.total_revenue:.2f}", class_name="text-xl font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("PIX Processados", class_name="text-sm text-muted-foreground"),
                    rx.text("247", class_name="text-xl font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4 w-full",
        ),
        
        # Transactions table
        transactions_table(),
        
        class_name="space-y-6 w-full",
    )