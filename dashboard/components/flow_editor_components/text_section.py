"""Text Content Section Component for Flow Editor"""
import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from .theme import THEME, section_header

def text_content_section(index: int, block: dict, is_payment: bool):
    """Renderiza a seção de conteúdo textual do bloco."""
    return rx.box(
        rx.hstack(
            section_header("align-left", "Conteúdo Textual"),
            rx.spacer(),
            # Badge Trigger (Oculto se for pagamento)
            rx.cond(
                ~is_payment,
                rx.popover.root(
                    rx.popover.trigger(
                        rx.text("+ Adicionar Badge", font_size="10px", weight="bold", color=THEME["accent"], cursor="pointer")
                    ),
                    rx.popover.content(
                        rx.vstack(
                            rx.text("URL da Badge (Topo)", size="1", weight="bold"),
                            rx.input(placeholder="http://...", on_change=FlowState.set_temp_badge_url, size="1"),
                            rx.button("Salvar", size="1", on_click=lambda: FlowState.insert_badge(index)),
                        )
                    )
                ),
                rx.fragment()
            ),
            width="100%", align="center", justify="between", mb="0"
        ),
        rx.text_area(
            value=block["text"],
            on_change=lambda val: FlowState.update_block_text(index, val),
            min_height="120px",
            variant="soft", color_scheme="gray",
            placeholder="Digite a mensagem que o usuário receberá...",
            bg=THEME["input_bg"],
            font_size="13px", line_height="1.6",
            resize="vertical"
        ),
        padding="16px", width="100%"
    )