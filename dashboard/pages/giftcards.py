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
        rx.heading("Catálogo de Gift Cards", size="5"),
        rx.text("Gerencie produtos, estoque e margens de lucro", size="3", color="gray"),
        
        # Action buttons
        rx.hstack(
            rx.button(
                "Adicionar Novo Produto",
                size="3",
                color_scheme="green",
                on_click=GiftCardState.set_show_add_giftcard_modal(True),
            ),
            rx.button(
                "Exportar Relatório",
                size="3",
                color_scheme="blue",
                on_click=rx.download(
                    data="giftcards_report",
                    filename="catalogo_giftcards.csv"
                ),
            ),
            spacing="4",
            align="center",
        ),
        
        # Summary statistics
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Total de Produtos", size="3", color="gray"),
                    rx.text(GiftCardState.gift_cards.length(), size="5", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Vendas Totais", size="3", color="gray"),
                    rx.text("156", size="5", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Lucro Estimado", size="3", color="gray"),
                    rx.text("R$ 12,450.00", size="5", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Estoque Total", size="3", color="gray"),
                    rx.text("1,247", size="5", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            gap="4",
            grid_template_columns=["repeat(2, 1fr)", "repeat(4, 1fr)"],
            width="100%",
        ),
        
        # Gift cards grid
                rx.grid(
                    rx.foreach(
                        GiftCardState.gift_cards,
                        lambda giftcard: rx.card(
                            rx.vstack(
                                rx.text(giftcard.name, weight="medium"),
                                rx.text(giftcard.category, color="gray"),
                                rx.text(f"R$ {giftcard.selling_price:.2f}", weight="bold"),
                                rx.text(f"Estoque: {giftcard.stock}", size="2"),
                                rx.text(f"Vendas: {giftcard.sold_count}", size="2"),
                                spacing="2",
                                align_items="start",
                            ),
                            width="100%",
                        )
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
        

        
        spacing="6",
        width="100%",
    )