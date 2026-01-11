# dashboard/pages/remarketing.py

import reflex as rx
from dashboard.components.ui.template.navbar import navbar
from dashboard.components.ui.template.sidebar import sidebar
from dashboard.backend.states.remarketing_state import RemarketingState, RemarketingBlock, RemarketingButton
from dashboard.components.flow_editor_components.theme import THEME

# --- COMPONENTE DE EDIÇÃO LOCAL ---
def render_remarketing_block(index: int, block: RemarketingBlock):
    """Renderiza o editor de bloco apontando para RemarketingState com tipagem forte."""
    return rx.card(
        rx.vstack(
            # Cabeçalho do Bloco
            rx.hstack(
                rx.badge("CTA Message", color_scheme="violet", variant="solid"),
                rx.spacer(),
                width="100%", align="center", mb="2"
            ),
            
            # 1. Seção de Texto
            rx.box(
                rx.text("Conteúdo da Mensagem", font_size="12px", weight="bold", color="gray"),
                rx.text_area(
                    value=block.text,
                    on_change=lambda val: RemarketingState.update_block_text(index, val),
                    min_height="100px",
                    variant="soft", placeholder="Digite sua mensagem...",
                ),
                width="100%", mb="3"
            ),

            # 2. Seção de Mídia
            rx.box(
                rx.hstack(
                    rx.text("Mídia (Opcional)", font_size="12px", weight="bold", color="gray"),
                    rx.select(
                        ["none", "image", "video"],
                        default_value=rx.cond(
                            block.image_url != "", "image", 
                            rx.cond(block.video_url != "", "video", "none")
                        ),
                        on_change=lambda val: RemarketingState.set_media_type(index, val),
                        size="1"
                    ),
                    justify="between", width="100%"
                ),
                rx.cond(
                    block.image_url != "",
                    rx.input(value=block.image_url, on_change=lambda v: RemarketingState.update_media_url(index, "image_url", v), placeholder="URL da Imagem"),
                ),
                rx.cond(
                    block.video_url != "",
                    rx.input(value=block.video_url, on_change=lambda v: RemarketingState.update_media_url(index, "video_url", v), placeholder="URL do Vídeo"),
                ),
                width="100%", mb="3", padding="10px", border="1px dashed #444", border_radius="8px"
            ),

            # 3. Seção de Botões
            rx.box(
                rx.hstack(
                    rx.text("Botões de Ação", font_size="12px", weight="bold", color="gray"),
                    rx.button("+ Linha", size="1", variant="ghost", on_click=lambda: RemarketingState.add_button_row(index)),
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
                                            rx.text("Texto do Botão"),
                                            rx.input(value=btn.text, on_change=lambda v: RemarketingState.update_button(index, r_idx, b_idx, "text", v), size="1"),
                                            rx.text("Tipo"),
                                            rx.select(["url", "callback"], default_value=btn.type, on_change=lambda v: RemarketingState.update_button(index, r_idx, b_idx, "type", v), size="1"),
                                            rx.cond(
                                                btn.type == "url",
                                                rx.input(value=btn.url, on_change=lambda v: RemarketingState.update_button(index, r_idx, b_idx, "url", v), placeholder="https://...", size="1"),
                                                rx.input(value=btn.callback, on_change=lambda v: RemarketingState.update_button(index, r_idx, b_idx, "callback", v), placeholder="goto_...", size="1")
                                            ),
                                            rx.button("Remover", color_scheme="red", size="1", width="100%", on_click=lambda: RemarketingState.remove_button(index, r_idx, b_idx))
                                        )
                                    )
                                )
                            ),
                            rx.button("+", size="1", variant="ghost", on_click=lambda: RemarketingState.add_button_to_row(index, r_idx))
                        )
                    ),
                    spacing="2", width="100%"
                ),
                width="100%"
            )
        ),
        width="100%", padding="4"
    )

# --- PÁGINA PRINCIPAL ---
@rx.page(route="/remarketing", title="Campanha de Remarketing")
def remarketing_page() -> rx.Component:
    return rx.box(
        rx.flex(
            sidebar(),
            rx.box(
                navbar(),
                rx.scroll_area(
                    rx.vstack(
                        rx.heading("📢 Remarketing de Recuperação", size="6", mb="4"),
                        
                        rx.grid(
                            # Coluna da Esquerda: Lista de Usuários
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Usuários Pendentes (>15min)", weight="bold"),
                                    rx.badge(RemarketingState.pending_users.length(), color_scheme="yellow"),
                                    rx.spacer(),
                                    rx.button("🔄 Atualizar Lista", on_click=RemarketingState.load_pending_users, size="1", variant="surface")
                                ),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Nome"),
                                            rx.table.column_header_cell("Valor"),
                                            rx.table.column_header_cell("Tempo"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            RemarketingState.pending_users,
                                            lambda user: rx.table.row(
                                                rx.table.cell(user["first_name"]),
                                                rx.table.cell(f"R$ {user['amount']}"),
                                                rx.table.cell(f"{user['minutes_pending']} min"),
                                            )
                                        )
                                    ),
                                    variant="surface",
                                    width="100%"
                                ),
                                padding="20px",
                                bg=THEME["panel_bg"],
                                border_radius="10px",
                                width="100%",
                                height="fit-content"
                            ),
                            
                            # Coluna da Direita: Editor e Ação
                            rx.vstack(
                                rx.text("Configuração da Mensagem (CTA)", weight="bold"),
                                
                                # Renderiza o editor usando o estado do Remarketing
                                rx.foreach(
                                    RemarketingState.editor_blocks,
                                    lambda block, idx: render_remarketing_block(idx, block)
                                ),
                                
                                rx.divider(my="4"),
                                
                                rx.box(
                                    rx.text("ℹ️ Variáveis disponíveis: {first_name}, {amount}", font_size="11px", color="gray", mb="2"),
                                    rx.button(
                                        rx.hstack(
                                            rx.icon("send", size=18),
                                            rx.text("Disparar Campanha Agora")
                                        ),
                                        on_click=RemarketingState.send_remarketing_campaign,
                                        width="100%",
                                        size="3",
                                        color_scheme="green"
                                    ),
                                    width="100%"
                                ),
                                width="100%"
                            ),
                            
                            columns="1fr 1fr",
                            gap="6",
                            width="100%"
                        ),
                        
                        padding="30px",
                        max_width="1200px",
                        margin="0 auto",
                        width="100%"
                    ),
                    type="always",
                    scrollbars="vertical"
                ),
                width="100%", display="flex", flex_direction="column",
            ),
            width="100%", display="flex",
        ),
        on_mount=RemarketingState.load_pending_users,
        background_color=THEME["app_bg"],
        min_height="100vh"
    )