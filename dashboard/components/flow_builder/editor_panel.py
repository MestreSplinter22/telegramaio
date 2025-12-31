import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from dashboard.components.flow_editor import flow_editor_component
from .styles import THEME, LABEL_STYLE


def editor_panel() -> rx.Component:
    """Painel de edição de dados (coluna direita) do flow builder."""
    return rx.box(
        # 1. Header Fixo
        rx.hstack(
            rx.box(
                rx.text("PROPRIEDADES", **LABEL_STYLE),
                rx.heading(FlowState.selected_screen_key, size="3", color="white", truncate=True),
                line_height="1.2"
            ),
            rx.spacer(),
            rx.segmented_control.root(
                rx.segmented_control.item(
                    rx.icon("layout-list", size=16), 
                    value="visual",
                    padding_x="2"
                ), 
                rx.segmented_control.item(
                    rx.icon("code", size=16), 
                    value="json",
                    padding_x="2"
                ),
                value=rx.cond(FlowState.visual_editor_mode, "visual", "json"),
                on_change=FlowState.set_editor_mode,
                size="1",
                variant="surface"
            ),
            width="100%",
            align="center",
            padding="16px",
            border_bottom=f"1px solid {THEME['border_subtle']}",
            bg=THEME["header_bg"],
            height="70px"
        ),
        
        # 2. Área de Conteúdo
        rx.box(
            rx.cond(
                FlowState.visual_editor_mode,
                flow_editor_component(), 
                rx.box(
                    rx.text_area(
                        value=FlowState.current_screen_content,
                        on_change=FlowState.update_content,
                        height="100%",
                        font_family="'Fira Code', monospace",
                        font_size="12px",
                        bg=rx.color("gray", 1), 
                        color="#cbd5e1",
                        border="none",
                        padding="16px",
                        _focus={"outline": "none"}
                    ),
                    height="100%",
                    width="100%"
                )
            ),
            flex="1",
            overflow="hidden",
            position="relative"
        ),
        
        # 3. Footer de Ação
        rx.box(
            rx.hstack(
                rx.hstack(
                    # CORREÇÃO 2: Removi o spinner que dependia de 'is_saving'
                    # Se quiser reativar depois, adicione is_saving: bool = False ao FlowState
                    rx.icon("check-circle", size=16, color="green"), 
                    rx.text(FlowState.status_message, font_size="11px", color=THEME["text_secondary"]),
                    spacing="2",
                    align="center"
                ),
                rx.spacer(),
                rx.button(
                    "Salvar Alterações",
                    icon="save",
                    color_scheme="indigo", 
                    variant="surface",
                    on_click=FlowState.save_current_screen,
                    size="2",
                    cursor="pointer"
                ),
                width="100%",
                align="center"
            ),
            padding="12px 16px",
            border_top=f"1px solid {THEME['border_subtle']}",
            bg=THEME["header_bg"]
        ),
        
        # Estilos Container Coluna 2
        bg=THEME["panel_bg"],
        border=f"1px solid {THEME['border_subtle']}",
        border_radius="lg",
        height="85vh",
        display="flex", 
        flex_direction="column",
        overflow="hidden",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    )