"""Gift cards catalog management page."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState
from ..templates import template



@template(route="/giftcards", title="Catálogo de Gift Cards")
def giftcards() -> rx.Component:
    """Gift cards catalog management page.

    Returns:
        The UI for the gift cards page.
    """
    return rx.vstack(
        rx.heading("Catálogo de Gift Cards", class_name="text-2xl font-bold text-foreground"),
        rx.text("Gerencie produtos, estoque e margens de lucro", class_name="text-base text-muted-foreground"),
        
        # Action buttons
        rx.hstack(
            rx.button(
                "Adicionar Novo Produto",
                class_name="bg-green-500 text-green-900 hover:bg-green-600 px-4 py-2 rounded-md text-sm font-medium",
                on_click=GiftCardState.set_show_add_giftcard_modal(True),
            ),
            rx.button(
                "Exportar Relatório",
                class_name="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md text-sm font-medium",
                on_click=rx.download(
                    data="giftcards_report",
                    filename="catalogo_giftcards.csv"
                ),
            ),
            class_name="items-center space-x-4",
        ),
        
        # Summary statistics
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Total de Produtos", class_name="text-sm text-muted-foreground"),
                    rx.text(GiftCardState.gift_cards.length(), class_name="text-xl font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Vendas Totais", class_name="text-sm text-muted-foreground"),
                    rx.text("156", class_name="text-xl font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Lucro Estimado", class_name="text-sm text-muted-foreground"),
                    rx.text("R$ 12,450.00", class_name="text-xl font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Estoque Total", class_name="text-sm text-muted-foreground"),
                    rx.text("1,247", class_name="text-xl font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            class_name="grid grid-cols-2 md:grid-cols-4 gap-4 w-full",
        ),
        
        # Gift cards grid
                rx.grid(
                    rx.foreach(
                        GiftCardState.gift_cards,
                        lambda giftcard: rx.card(
                            rx.vstack(
                                rx.text(giftcard.name, class_name="font-medium text-foreground"),
                                rx.text(giftcard.category, class_name="text-muted-foreground"),
                                rx.text(f"R$ {giftcard.selling_price:.2f}", class_name="font-bold text-foreground"),
                                rx.text(f"Estoque: {giftcard.stock}", class_name="text-xs text-muted-foreground"),
                                rx.text(f"Vendas: {giftcard.sold_count}", class_name="text-xs text-muted-foreground"),
                                class_name="space-y-2 items-start",
                            ),
                            class_name="w-full",
                        )
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 w-full",
                ),
        

        
        class_name="space-y-6 w-full",
    )