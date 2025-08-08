"""Bot management and monitoring page."""

import reflex as rx
from ..backend.giftcard_state import GiftCardState
from ..templates import template



@template(route="/bot-management", title="Gerenciamento do Bot")
def bot_management() -> rx.Component:
    """Bot management and monitoring page.

    Returns:
        The UI for the bot management page.
    """
    return rx.vstack(
        rx.heading("Gerenciamento do Bot Telegram", size="5"),
        rx.text("Monitoramento em tempo real do bot e análise de uso", size="3", color="gray"),
        
        # Bot status overview
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("circle", size=16, color="green"),
                        rx.text("Status", size="3", color="gray"),
                        spacing="2",
                    ),
                    rx.text("Online", size="4", weight="bold", color="green"),
                    spacing="1",
                ),
                padding="4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Usuários Ativos", size="3", color="gray"),
                    rx.text("342", size="4", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Mensagens/Hoje", size="3", color="gray"),
                    rx.text("1.2K", size="4", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Tempo Resposta", size="3", color="gray"),
                    rx.text("1.2s", size="4", weight="bold"),
                    spacing="1",
                ),
                padding="4",
            ),
            gap="4",
            grid_template_columns=["repeat(2, 1fr)", "repeat(4, 1fr)"],
            width="100%",
        ),
        
        # Control buttons
        rx.hstack(
            rx.button(
                "Reiniciar Bot",
                size="3",
                color_scheme="yellow",
                on_click=GiftCardState.restart_bot,
            ),
            rx.button(
                "Limpar Logs",
                size="3",
                color_scheme="red",
                on_click=GiftCardState.clear_logs,
            ),
            rx.button(
                "Exportar Logs",
                size="3",
                color_scheme="blue",
                on_click=rx.download(
                    data="bot_logs",
                    filename="logs_telegram_bot.json"
                ),
            ),
            spacing="4",
            align="center",
        ),
        
        # Bot metrics charts
        rx.card(
            rx.vstack(
                rx.text("Métricas do Bot", size="4", weight="medium"),
                rx.text("Gráficos de uso e performance", size="2", color="gray"),
                spacing="2",
            ),
            padding="4",
            width="100%",
        ),
        
        # Bot commands usage
        rx.card(
            rx.vstack(
                rx.text("Comandos Mais Usados", size="4", weight="medium"),
                rx.vstack(
                    rx.hstack(
                        rx.text("/start", size="3"),
                        rx.spacer(),
                        rx.text("245 vezes", size="2", color="gray"),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("/comprar", size="3"),
                        rx.spacer(),
                        rx.text("189 vezes", size="2", color="gray"),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("/saldo", size="3"),
                        rx.spacer(),
                        rx.text("156 vezes", size="2", color="gray"),
                        width="100%",
                    ),
                    spacing="2",
                ),
                spacing="3",
            ),
            padding="4",
            width="100%",
        ),
        
        # Bot logs
        rx.card(
            rx.vstack(
                rx.text("Logs do Bot", size="4", weight="medium"),
                rx.text("Últimas atividades do bot", size="2", color="gray"),
                rx.text(
                    "2024-01-15 10:30:45 - Bot iniciado\n2024-01-15 10:31:12 - Novo usuário: @usuario123\n2024-01-15 10:32:01 - Compra realizada: R$ 50.00\n2024-01-15 10:33:28 - PIX confirmado",
                    font_family="monospace",
                    size="2",
                    white_space="pre-wrap",
                ),
                spacing="2",
            ),
            padding="4",
            width="100%",
        ),
        
        spacing="6",
        width="100%",
    )