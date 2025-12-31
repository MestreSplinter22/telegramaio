"""Theme constants for Flow Editor"""
import reflex as rx

# --- DESIGN SYSTEM (Clean & Professional) ---
THEME = {
    "panel_bg": rx.color("gray", 1),        # Fundo do editor (mais escuro/neutro)
    "card_bg": rx.color("gray", 2),         # Fundo do bloco de mensagem
    "section_bg": rx.color("gray", 3),      # Fundo para áreas agrupadas (linhas de botões)
    "input_bg": rx.color("gray", 1),        # Fundo de inputs para criar profundidade "cutout"
    "border_subtle": rx.color("gray", 4),   # Divisórias quase invisíveis
    "border_strong": rx.color("gray", 6),   # Bordas de definição
    "text_primary": rx.color("gray", 12),   # Texto principal
    "text_secondary": rx.color("gray", 10), # Instruções/Labels
    "accent": rx.color("indigo", 9),        # Cor de destaque pontual
    "payment_accent": rx.color("green", 9), # Cor destaque para pagamento
}

SECTION_TITLE_STYLE = {
    "font_size": "10px",
    "font_weight": "bold",
    "color": THEME["text_secondary"],
    "letter_spacing": "0.08em",
    "text_transform": "uppercase",
    "display": "flex",
    "align_items": "center",
    "gap": "6px",
}

def section_header(icon: str, title: str):
    """Gera um cabeçalho de seção limpo e padronizado."""
    return rx.hstack(
        rx.icon(icon, size=14, color=THEME["text_secondary"]),
        rx.text(title, **SECTION_TITLE_STYLE),
        width="100%",
        padding_bottom="8px",
        border_bottom=f"1px solid {THEME['border_subtle']}",
        margin_bottom="12px"
    )