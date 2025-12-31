"""Payment Section Component for Flow Editor"""
import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from .theme import THEME, section_header

def payment_section(index: int, block: dict):
    """Renderiza a seção de pagamento do bloco."""
    return rx.box(
        section_header("credit-card", "Parâmetros da Transação"),
        rx.grid(
            rx.box(
                rx.text("Gateway", font_size="9px", color=THEME["text_secondary"], mb="1"),
                rx.select(
                    ["suitpay", "efibank", "openpix"],
                    value=block["gateway"],
                    on_change=lambda val: FlowState.update_payment_gateway(index, val),
                    size="2", variant="soft", color_scheme="gray", width="100%",
                    bg=THEME["input_bg"]
                ),
            ),
            rx.box(
                rx.text("Valor (R$)", font_size="9px", color=THEME["text_secondary"], mb="1"),
                rx.input(
                    type="number",
                    step="0.01",
                    value=block["amount"].to_string(),
                    on_change=lambda val: FlowState.update_payment_amount(index, val),
                    size="2", variant="soft", color_scheme="gray", width="100%",
                    bg=THEME["input_bg"]
                ),
            ),
            columns="2", gap="4", width="100%"
        ),
        padding="16px", width="100%"
    )