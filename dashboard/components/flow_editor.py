import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from .flow_editor_components.block_component import render_block

def flow_editor_component():
    """Componente Principal do Editor - Container Global."""
    from .flow_editor_components.theme import THEME
    
    # Verificação segura do tipo do primeiro bloco para ocultar o botão "Adicionar Mensagem"
    # Assumimos que nós de pagamento são blocos únicos
    first_block_is_payment = rx.cond(
        FlowState.editor_blocks.length() > 0,
        FlowState.editor_blocks[0]["type"] == "payment",
        False
    )

    return rx.scroll_area(
        rx.vstack(
            rx.foreach(
                FlowState.editor_blocks,
                lambda block, idx: render_block(idx, block)
            ),
            
            # Botão Final de Adição (Oculto se for um nó de pagamento)
            rx.cond(
                ~first_block_is_payment,
                rx.button(
                    rx.hstack(
                        rx.icon("plus-circle", size=20),
                        rx.text("Adicionar Nova Mensagem ao Fluxo", font_size="14px", weight="bold")
                    ),
                    on_click=FlowState.add_block,
                    size="4", variant="outline", color_scheme="gray",
                    width="100%", height="60px",
                    margin_top="10px", margin_bottom="120px", 
                    border_style="dashed", border_width="2px",
                    _hover={"bg": rx.color("gray", 3), "border_color": THEME["text_secondary"]}
                ),
                rx.fragment() # Não mostra o botão
            ),
            
            spacing="0",
            width="100%",
            padding="24px",
            max_width="900px", 
            margin="0 auto"    
        ),
        bg=THEME["panel_bg"],
        type="always",
        scrollbars="vertical",
        style={"height": "100%"}
    )