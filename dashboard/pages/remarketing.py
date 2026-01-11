# dashboard/pages/remarketing.py

import reflex as rx
from dashboard.components.ui.template.navbar import navbar
from dashboard.components.ui.template.sidebar import sidebar
from dashboard.backend.states.remarketing_state import RemarketingState, RemarketingBlock
from dashboard.components.flow_editor_components.theme import THEME

# --- COMPONENTES AUXILIARES ---

def media_selector(index: int, block: RemarketingBlock):
    return rx.vstack(
        rx.hstack(
            rx.text("Mídia Visual", font_size="11px", weight="bold", color="gray"),
            rx.select(
                ["none", "image", "video"],
                value=rx.cond(block.image_url != "", "image", rx.cond(block.video_url != "", "video", "none")),
                on_change=lambda val: RemarketingState.set_media(index, val),
                size="1"
            ),
            justify="between", width="100%", mt="2"
        ),
        rx.cond(
            block.image_url != "",
            rx.input(value=block.image_url, on_change=lambda v: RemarketingState.update_field(index, "image_url", v), placeholder="URL da Imagem")
        ),
        rx.cond(
            block.video_url != "",
            rx.input(value=block.video_url, on_change=lambda v: RemarketingState.update_field(index, "video_url", v), placeholder="URL do Vídeo")
        ),
        width="100%"
    )

def buttons_editor_full(index: int, block: RemarketingBlock):
    return rx.vstack(
        rx.hstack(
            rx.text("Botões", font_size="11px", weight="bold"),
            rx.button("+ Linha", size="1", variant="ghost", on_click=lambda: RemarketingState.add_btn_row(index)),
            justify="between", width="100%"
        ),
        rx.vstack(
            rx.foreach(
                block.buttons,
                lambda row, r_idx: rx.hstack(
                    rx.foreach(
                        row,
                        lambda btn, b_idx: rx.popover.root(
                            rx.popover.trigger(rx.button(btn.text, size="1", variant="outline")),
                            rx.popover.content(
                                rx.vstack(
                                    rx.text("Texto"),
                                    rx.input(value=btn.text, on_change=lambda v: RemarketingState.update_btn(index, r_idx, b_idx, "text", v), size="1"),
                                    rx.text("URL"),
                                    rx.input(value=btn.url, on_change=lambda v: RemarketingState.update_btn(index, r_idx, b_idx, "url", v), placeholder="https://...", size="1"),
                                    rx.button("Remover", color_scheme="red", size="1", on_click=lambda: RemarketingState.remove_btn(index, r_idx, b_idx), width="100%")
                                )
                            )
                        )
                    ),
                    rx.button("+", size="1", variant="ghost", on_click=lambda: RemarketingState.add_btn(index, r_idx))
                )
            ),
            spacing="2", width="100%"
        ),
        width="100%", padding="8px", border="1px dashed #444", border_radius="6px", mt="2"
    )

# --- RENDERIZADORES ESPECÍFICOS POR NÓ ---

def render_node_1(index: int, block: RemarketingBlock):
    """Nó 1: CTA. Botão Único (Título apenas)."""
    return rx.vstack(
        rx.text("Mensagem de Abordagem", font_size="11px", weight="bold"),
        rx.text_area(
            value=block.text,
            on_change=lambda val: RemarketingState.update_field(index, "text", val),
            min_height="100px", variant="soft",
            placeholder="Texto convidativo..."
        ),
        
        media_selector(index, block),
        
        rx.box(
            rx.text("Botão de Ação (GOTO Próximo Passo)", font_size="11px", weight="bold", color="violet", mt="3"),
            rx.input(
                value=block.buttons[0][0].text,
                on_change=lambda val: RemarketingState.update_first_button_text(index, val),
                placeholder="Ex: 💳 Quero Pagar Agora",
            ),
            rx.text("Este botão levará o usuário para a etapa de pagamento.", font_size="10px", color="gray", mt="1"),
            padding="10px", bg=rx.color("violet", 3), border_radius="6px", width="100%"
        ),
        width="100%"
    )

def render_node_2(index: int, block: RemarketingBlock):
    """Nó 2: Pagamento. Sem botões, Configuração Financeira."""
    return rx.vstack(
        rx.text("Legenda do QR Code", font_size="11px", weight="bold"),
        rx.text_area(
            value=block.text,
            on_change=lambda val: RemarketingState.update_field(index, "text", val),
            min_height="80px", variant="soft",
        ),
        
        rx.box(
            rx.text("Configuração Financeira", weight="bold", font_size="12px", color=THEME["payment_accent"]),
            rx.grid(
                rx.vstack(
                    rx.text("Gateway", font_size="11px"),
                    rx.select(["openpix", "efi", "suitpay"], value=block.gateway, on_change=lambda v: RemarketingState.update_field(index, "gateway", v), size="2")
                ),
                rx.vstack(
                    rx.text("Valor da Oferta (R$)", font_size="11px"),
                    rx.input(
                        value=block.amount.to(str), 
                        on_change=lambda v: RemarketingState.update_field(index, "amount", v),
                        placeholder="0.00 = Pendente",
                        type="number"
                    ),
                ),
                columns="2", gap="2", mt="2"
            ),
            rx.text("Se Valor for 0, o sistema cobrará o valor pendente original.", font_size="10px", color="gray", mt="1"),
            width="100%", bg=rx.color("green", 3), padding="10px", border_radius="6px", mt="2"
        ),
        width="100%"
    )

def render_node_3(index: int, block: RemarketingBlock):
    """Nó 3: Sucesso. Totalmente flexível."""
    return rx.vstack(
        rx.text("Mensagem de Confirmação", font_size="11px", weight="bold"),
        rx.text_area(
            value=block.text,
            on_change=lambda val: RemarketingState.update_field(index, "text", val),
            min_height="100px", variant="soft",
        ),
        media_selector(index, block),
        buttons_editor_full(index, block),
        width="100%"
    )

def render_remarketing_node(index: int, block: RemarketingBlock):
    """Renderiza o cartão correto baseado no índice/tipo."""
    
    scheme = rx.cond(block.type == "message", "violet", rx.cond(block.type == "payment", "orange", "green"))
    icon_comp = rx.cond(block.type == "message", rx.icon("message-circle", size=14),
                rx.cond(block.type == "payment", rx.icon("credit-card", size=14), rx.icon("check-circle", size=14)))

    return rx.box(
        rx.cond(index > 0, rx.center(rx.icon("arrow-down", size=20, color=THEME["border_strong"]), py="2"), rx.fragment()),
        
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.badge(icon_comp, size="1", color_scheme=scheme, variant="solid"),
                    rx.text(block.title, weight="bold", font_size="13px"),
                    rx.spacer(),
                    width="100%", align="center", mb="3", border_bottom=f"1px solid {THEME['border_subtle']}", pb="2"
                ),
                rx.cond(block.type == "message", render_node_1(index, block)),
                rx.cond(block.type == "payment", render_node_2(index, block)),
                rx.cond(block.type == "webhook", render_node_3(index, block)),
                width="100%"
            ),
            width="100%", bg=THEME["card_bg"], border=f"1px solid {THEME['border_subtle']}", padding="4"
        ),
        width="100%"
    )

@rx.page(route="/remarketing", title="Fluxo de Remarketing")
def remarketing_page() -> rx.Component:
    return rx.box(
        rx.flex(
            sidebar(),
            rx.box(
                navbar(),
                rx.scroll_area(
                    rx.vstack(
                        rx.heading("📢 Remarketing Estruturado", size="6", mb="1"),
                        rx.text("Campanha de 3 etapas: Oferta -> Pagamento -> Sucesso.", color="gray", size="2", mb="6"),
                        
                        rx.grid(
                            # COLUNA ESQUERDA: LISTA COM SELEÇÃO
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Alvos (>15min)", weight="bold"),
                                    rx.badge(RemarketingState.pending_users.length(), color_scheme="blue"),
                                    rx.spacer(),
                                    rx.button("🔄 Atualizar", on_click=RemarketingState.load_pending_users, size="1")
                                ),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            # Checkbox "Selecionar Todos"
                                            rx.table.column_header_cell(
                                                rx.checkbox(
                                                    checked=RemarketingState.all_selected_checked,
                                                    on_change=RemarketingState.toggle_all
                                                )
                                            ),
                                            rx.table.column_header_cell("Nome"),
                                            rx.table.column_header_cell("R$")
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            RemarketingState.pending_users,
                                            lambda user: rx.table.row(
                                                # Checkbox Individual
                                                rx.table.cell(
                                                    rx.checkbox(
                                                        checked=RemarketingState.selected_users.contains(user["telegram_id"]),
                                                        on_change=lambda val: RemarketingState.toggle_user(user["telegram_id"], val)
                                                    )
                                                ),
                                                rx.table.cell(user["first_name"]),
                                                rx.table.cell(user["amount"])
                                            )
                                        )
                                    ),
                                    variant="surface", size="1", width="100%"
                                ),
                                rx.text(
                                    f"Selecionados: ", rx.text(RemarketingState.selected_count, weight="bold", as_="span"),
                                    font_size="12px", color="gray", mt="2"
                                ),
                                padding="15px", bg=THEME["panel_bg"], border_radius="10px", width="100%"
                            ),
                            
                            # COLUNA DIREITA: EDITOR ESTRUTURADO
                            rx.vstack(
                                rx.foreach(
                                    RemarketingState.editor_blocks,
                                    lambda block, idx: render_remarketing_node(idx, block)
                                ),
                                rx.divider(my="6"),
                                rx.button(
                                    rx.hstack(
                                        rx.icon("send", size=16), 
                                        rx.text(f"DISPARAR ({RemarketingState.selected_count})")
                                    ),
                                    on_click=RemarketingState.send_remarketing_campaign,
                                    width="100%", size="3", color_scheme="green",
                                    disabled=RemarketingState.selected_count == 0
                                ),
                                width="100%"
                            ),
                            
                            columns="1fr 2fr", gap="8", width="100%"
                        ),
                        padding="30px", max_width="1200px", margin="0 auto"
                    ),
                    type="always", scrollbars="vertical"
                ),
                width="100%", display="flex", flex_direction="column"
            ),
            width="100%", display="flex"
        ),
        on_mount=RemarketingState.load_pending_users,
        background_color=THEME["app_bg"],
        min_height="100vh"
    )