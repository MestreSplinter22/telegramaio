"""Transactions table component."""

import reflex as rx
from ...backend.states.transactions import TransactionState
from ...components.ui.card import card

def transaction_status_badge(status: rx.Var) -> rx.Component:
    """Transaction status badge com lógica condicional do Reflex."""
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
    """Componente de tabela de transações corrigido."""
    return card(
        rx.vstack(
            rx.hstack(
                rx.text("Transações", class_name="text-lg font-medium text-foreground"),
                rx.spacer(),
                # Exibe a contagem total baseada no estado filtrado
                rx.text(
                    f"Exibindo: {TransactionState.filtered_transactions.length()} registros", 
                    class_name="text-sm text-muted-foreground"
                ),
                class_name="w-full",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ID", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Tipo", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Valor", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Status", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Data", class_name="text-sm font-medium text-foreground"),
                        rx.table.column_header_cell("Ações", class_name="text-sm font-medium text-foreground"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        TransactionState.filtered_transactions,
                        lambda transaction: rx.table.row(
                            # Correção 1: ID int para string para evitar erros de renderização
                            rx.table.cell(transaction.id.to_string(), class_name="text-sm text-foreground"),
                            rx.table.cell(transaction.type, class_name="text-sm text-foreground"),
                            # Nota: Formatação de float (.2f) funciona melhor via f-string ou ComputedVar no State
                            rx.table.cell(f"R$ {transaction.amount.to_string()}", class_name="text-sm text-foreground"),
                            rx.table.cell(transaction_status_badge(transaction.status)),
                            # Correção 2: Uso do campo 'timestamp' e conversão para string
                            rx.table.cell(transaction.timestamp.to_string(), class_name="text-sm text-foreground"),
                            rx.table.cell(
                                rx.button(
                                    "Detalhes",
                                    size="1",
                                    on_click=lambda: TransactionState.set_selected_transaction(transaction),
                                    class_name="text-xs cursor-pointer",
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