import reflex as rx
from dashboard.backend.states.flow_state import FlowState

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

def render_block(index: int, block: dict):
    """
    Renderiza o Bloco Principal. Adapta a UI se for 'payment'.
    """
    has_image = block.contains("image_url")
    has_video = block.contains("video_url")
    media_type = rx.cond(has_image, "image", rx.cond(has_video, "video", "none"))
    buttons_rows = block["buttons"].to(list)
    
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
                        rx.box(
                            section_header("image", "Mídia & Anexos"),
                            rx.flex(
                                rx.select(
                                    ["none", "image", "video"],
                                    value=media_type,
                                    on_change=lambda val: FlowState.set_media_type(index, val),
                                    size="2", variant="soft", color_scheme="gray",
                                    width="120px", flex_shrink="0"
                                ),
                                rx.cond(
                                    media_type != "none",
                                    rx.input(
                                        value=rx.cond(media_type == "image", block["image_url"], block["video_url"]),
                                        placeholder="Cole a URL do arquivo aqui...",
                                        on_change=lambda val: FlowState.update_media_url(index, rx.cond(media_type=="image", "image_url", "video_url"), val),
                                        variant="soft", color_scheme="gray", size="2", width="100%",
                                        bg=THEME["input_bg"]
                                    )
                                ),
                                gap="3", width="100%", align="center"
                            ),
                            padding="16px", width="100%"
                        ),
                        rx.divider(color_scheme="gray", size="4", opacity="0.3"),
                    ),
                    rx.fragment() # Renderiza nada se for pagamento
                ),

                # 2. NOVO: SEÇÃO DE PAGAMENTO (Apenas se FOR pagamento)
                rx.cond(
                    is_payment,
                    rx.fragment(
                        rx.box(
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
                        ),
                        rx.divider(color_scheme="gray", size="4", opacity="0.3"),
                    ),
                    rx.fragment()
                ),

                # 3. SEÇÃO DE TEXTO
                rx.box(
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
                ),

                rx.divider(color_scheme="gray", size="4", opacity="0.3"),

                # 4. SEÇÃO DE INTERAÇÕES (Botões)
                rx.box(
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
                ),

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

def flow_editor_component():
    """Componente Principal do Editor - Container Global."""
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