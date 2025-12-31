"""Main Block Component for Flow Editor"""
import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from .theme import THEME
from .media_section import media_section
from .payment_section import payment_section
from .text_section import text_content_section
from .buttons_section import buttons_section

def render_block(index: int, block: dict):
    """
    Renderiza o Bloco Principal. Adapta a UI se for 'payment'.
    """
    # Verifica se é um nó de pagamento
    is_payment = block["type"] == "payment"
    
    return rx.box(
        rx.vstack(
            # --- HEADER DO CARD ---
            rx.hstack(
                rx.center(
                    rx.text(f"{index + 1}", color="white", font_weight="bold", font_size="14px"),
                    bg=rx.cond(is_payment, THEME["payment_accent"], THEME["accent"]), 
                    width="28px", height="28px", border_radius="6px",
                    box_shadow="0 1px 2px rgba(0,0,0,0.1)"
                ),
                rx.vstack(
                    rx.text(
                        rx.cond(is_payment, "Configuração de Pagamento", "Mensagem do Fluxo"),
                        size="2", weight="bold", color=THEME["text_primary"]
                    ),
                    rx.text("Configure o conteúdo e opções", size="1", color=THEME["text_secondary"]),
                    spacing="0", align_items="start"
                ),
                rx.spacer(),
                rx.tooltip(
                    rx.icon_button(
                        "trash-2", variant="surface", color_scheme="gray", size="2",
                        on_click=lambda: FlowState.remove_block(index),
                        _hover={"color": "red", "bg": rx.color("red", 3)}
                    ),
                    content="Excluir este bloco"
                ),
                width="100%", align="center", 
                padding="12px 16px",
                border_bottom=f"1px solid {THEME['border_subtle']}",
                bg=rx.color("gray", 3)
            ),
            
            # --- CORPO DO CARD ---
            rx.vstack(
                # 1. SEÇÃO DE MÍDIA (Apenas se NÃO for pagamento)
                rx.cond(
                    ~is_payment,
                    rx.fragment(
                        media_section(index, block),
                        rx.divider(color_scheme="gray", size="4", opacity="0.3"),
                    ),
                    rx.fragment() # Renderiza nada se for pagamento
                ),

                # 2. NOVO: SEÇÃO DE PAGAMENTO (Apenas se FOR pagamento)
                rx.cond(
                    is_payment,
                    rx.fragment(
                        payment_section(index, block),
                        rx.divider(color_scheme="gray", size="4", opacity="0.3"),
                    ),
                    rx.fragment()
                ),

                # 3. SEÇÃO DE TEXTO
                text_content_section(index, block, is_payment),

                rx.divider(color_scheme="gray", size="4", opacity="0.3"),

                # 4. SEÇÃO DE INTERAÇÕES (Botões)
                buttons_section(index, block),

                spacing="0", width="100%", align_items="start"
            ),
        ),
        
        bg=THEME["card_bg"],
        border=f"1px solid {THEME['border_subtle']}",
        border_radius="lg",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        overflow="hidden",
        width="100%",
        margin_bottom="32px"
    )