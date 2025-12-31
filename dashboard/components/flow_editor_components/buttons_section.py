"""Buttons Section Component for Flow Editor"""
import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from .theme import THEME, section_header
from .button_item import render_button_item

def buttons_section(index: int, block: dict):
    """Renderiza a seção de botões de interação do bloco."""
    buttons_rows = block["buttons"].to(list)
    
    return rx.box(
        rx.hstack(
            section_header("mouse-pointer-2", "Botões de Interação"),
            rx.spacer(),
            rx.button(
                "Nova Linha", 
                on_click=lambda: FlowState.add_button_row(index),
                variant="surface", size="1", color_scheme="gray",
                cursor="pointer"
            ),
            width="100%", align="center", mb="4"
        ),
        
        rx.vstack(
            rx.foreach(
                buttons_rows,
                lambda row, r_idx: rx.box(
                    rx.hstack(
                        rx.vstack(
                            rx.icon("arrow-right", size=12, color=THEME["text_secondary"]),
                            rx.text(f"Linha {r_idx + 1}", font_size="9px", font_weight="bold", color=THEME["text_secondary"], orientation="vertical"),
                            align="center", spacing="1", width="30px"
                        ),
                        rx.scroll_area(
                            rx.flex(
                                rx.foreach(
                                    row.to(list),
                                    lambda btn, b_idx: render_button_item(index, r_idx, b_idx, btn)
                                ),
                                rx.button(
                                    rx.icon("plus", size=18),
                                    variant="ghost", color_scheme="gray",
                                    height="100%", min_height="160px", width="40px",
                                    border=f"1px dashed {THEME['border_strong']}",
                                    on_click=lambda: FlowState.add_button_to_row(index, r_idx),
                                    _hover={"bg": THEME["section_bg"], "border_color": THEME["text_primary"]}
                                ),
                                gap="3", padding_bottom="4px", align="stretch"
                            ),
                            type="auto", scrollbars="horizontal", style={"max-width": "100%"}
                        ),
                        align="start", spacing="2", width="100%"
                    ),
                    padding="12px",
                    bg=THEME["section_bg"],
                    border_radius="md",
                    border=f"1px solid {THEME['border_subtle']}",
                    width="100%"
                )
            ),
            spacing="3", width="100%"
        ),
        padding="16px", width="100%"
    )