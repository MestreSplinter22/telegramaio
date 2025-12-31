"""Button Item Component for Flow Editor"""
import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from .theme import THEME

def render_button_item(block_idx: int, row_idx: int, btn_idx: int, btn_data: dict):
    """
    Renderiza um botão individual com layout vertical limpo.
    """
    btn = btn_data.to(dict)
    is_url = btn.contains("url")
    
    return rx.box(
        rx.vstack(
            # Topo: Identificador e Ação de Remover
            rx.hstack(
                rx.box(
                    rx.text(f"#{btn_idx + 1}", font_size="9px", font_weight="bold", color="white"),
                    bg=THEME["text_secondary"], padding_x="6px", border_radius="4px",
                ),
                rx.spacer(),
                rx.icon_button(
                    "x", size="1", variant="ghost", color_scheme="gray",
                    on_click=lambda: FlowState.remove_button(block_idx, row_idx, btn_idx),
                    cursor="pointer", height="18px", width="18px", padding="0",
                    opacity="0.6", _hover={"opacity": "1", "color": "red", "bg": rx.color("red", 3)}
                ),
                width="100%", align="center", mb="2"
            ),
            
            # Campos de Edição
            rx.vstack(
                rx.box(
                    rx.text("Label", font_size="9px", color=THEME["text_secondary"], mb="1"),
                    rx.input(
                        value=btn["text"],
                        on_change=lambda val: FlowState.update_button(block_idx, row_idx, btn_idx, "text", val),
                        size="1", variant="soft", color_scheme="gray", width="100%",
                        bg=THEME["input_bg"], placeholder="Texto..."
                    ),
                    width="100%"
                ),
                rx.box(
                    rx.text("Tipo", font_size="9px", color=THEME["text_secondary"], mb="1"),
                    rx.select(
                        ["callback", "url"],
                        value=rx.cond(is_url, "url", "callback"),
                        on_change=lambda val: FlowState.update_button(block_idx, row_idx, btn_idx, "type", val),
                        size="1", variant="soft", color_scheme="gray", width="100%",
                        bg=THEME["input_bg"]
                    ),
                    width="100%"
                ),
                rx.box(
                    rx.text("Destino", font_size="9px", color=THEME["text_secondary"], mb="1"),
                    rx.cond(
                        is_url,
                        rx.input(
                            value=btn["url"], placeholder="https://...",
                            on_change=lambda val: FlowState.update_button(block_idx, row_idx, btn_idx, "url", val),
                            size="1", variant="soft", color_scheme="gray", width="100%", bg=THEME["input_bg"]
                        ),
                        rx.input(
                            value=btn["callback"], placeholder="step_id...",
                            on_change=lambda val: FlowState.update_button(block_idx, row_idx, btn_idx, "callback", val),
                            size="1", variant="soft", color_scheme="gray", width="100%", bg=THEME["input_bg"]
                        )
                    ),
                    width="100%"
                ),
                spacing="2", width="100%"
            ),
            spacing="0", width="100%"
        ),
        bg=rx.color("gray", 3),
        border=f"1px solid {THEME['border_subtle']}",
        border_radius="md",
        padding="10px",
        width="150px",
        flex_shrink="0",
        transition="all 0.2s",
        _hover={"border_color": THEME["border_strong"], "box_shadow": "0 2px 8px rgba(0,0,0,0.05)"}
    )