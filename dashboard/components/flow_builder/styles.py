import reflex as rx

# --- DESIGN SYSTEM COMPARTILHADO ---
THEME = {
    "app_bg": rx.color("gray", 1),          # Fundo geral da aplicação
    "panel_bg": rx.color("gray", 2),        # Fundo dos painéis (Canvas/Editor)
    "header_bg": rx.color("gray", 2),       # Fundo dos headers (Toolbars)
    "border_subtle": rx.color("gray", 4),   # Bordas divisórias
    "border_strong": rx.color("gray", 6),   # Bordas de destaque
    "text_primary": rx.color("gray", 12),   # Texto principal
    "text_secondary": rx.color("gray", 10), # Labels e instruções
    "accent": rx.color("indigo", 9),        # Ação principal (Botões/Destaques)
    "input_bg": rx.color("gray", 3),        # Inputs
}

# Estilos de Texto Utilitários
LABEL_STYLE = {
    "font_size": "10px",
    "font_weight": "bold",
    "color": THEME["text_secondary"],
    "letter_spacing": "0.05em",
    "text_transform": "uppercase",
}