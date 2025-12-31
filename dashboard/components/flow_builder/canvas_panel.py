import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from .styles import THEME, LABEL_STYLE

# Importamos do nosso wrapper local
from dashboard.components.react_flow_wrapper import ReactFlow, Background, Controls, MiniMap


def canvas_panel() -> rx.Component:
    """Painel de visualização interativa (coluna esquerda) do flow builder."""
    return rx.box(
        # 1. Header (Toolbar)
        rx.hstack(
            rx.box(
                rx.text("VISUALIZAÇÃO", **LABEL_STYLE),
                rx.heading("Fluxo Interativo", size="3", color=THEME["text_primary"]),
                line_height="1.2"
            ),
            rx.spacer(),
            # Controles do Header
            rx.hstack(
                rx.badge("React Flow", color_scheme="indigo", variant="surface"),
                
                # BOTÃO NOVO: Criar Sequência de Pagamento
                rx.tooltip(
                    rx.icon_button(
                        "credit-card", 
                        on_click=FlowState.add_payment_sequence, 
                        variant="soft", 
                        color_scheme="green", 
                        size="2"
                    ),
                    content="Gerar Sequência de Pagamento (Nó Duplo)"
                ),

                rx.tooltip(
                    rx.icon_button(
                        "rotate-cw", 
                        on_click=FlowState.calculate_interactive_layout, 
                        variant="soft", color_scheme="gray", size="2"
                    ),
                    content="Reorganizar Layout Automaticamente"
                ),
                spacing="3"
            ),
            width="100%",
            align="center",
            padding="16px",
            border_bottom=f"1px solid {THEME['border_subtle']}",
            bg=THEME["header_bg"],
            height="70px"
        ),
        
        # 2. Área do Canvas (React Flow)
        rx.box(
            ReactFlow.create(
                # Plugins visuais
                Background.create(
                    variant="dots", 
                    gap=24, 
                    size=1, 
                    # CORREÇÃO 1: Convertendo cor para string
                    # Alterado para cinza claro para melhor design do canvas
                    color=str(rx.color("white", 3)) 
                ),
                
                # Props Lógicas
                nodes=FlowState.nodes,
                edges=FlowState.edges,
                on_node_click=FlowState.on_node_click,
                fit_view=True,
            ),
            width="100%",
            flex="1", 
            bg=THEME["panel_bg"], 
            overflow="hidden"
        ),
        
        # 3. Footer de Ação
        rx.box(
            rx.hstack(
                rx.icon("plus-square", size=18, color=THEME["text_secondary"]),
                rx.input(
                    placeholder="Nome da nova tela (ID único)...", 
                    value=FlowState.new_screen_name, 
                    on_change=FlowState.set_new_screen_name,
                    size="2", 
                    variant="soft", 
                    bg=THEME["input_bg"],
                    color_scheme="gray",
                    width="100%",
                    border=f"1px solid {THEME['border_subtle']}",
                    _focus={"border_color": THEME["accent"]}
                ),
                rx.button(
                    "Criar Tela", 
                    icon="plus",
                    on_click=FlowState.add_new_screen, 
                    size="2", 
                    variant="solid",
                    color_scheme="indigo",
                    cursor="pointer"
                ),
                width="100%",
                align="center",
                spacing="3"
            ),
            padding="12px 16px",
            border_top=f"1px solid {THEME['border_subtle']}",
            bg=THEME["header_bg"]
        ),
        
        # Estilos Container Coluna 1
        height="85vh",
        display="flex",
        flex_direction="column",
        bg=THEME["panel_bg"],
        border=f"1px solid {THEME['border_subtle']}",
        border_radius="lg",
        overflow="hidden",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    )