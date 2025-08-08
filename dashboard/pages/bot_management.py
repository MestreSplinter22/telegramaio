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
        rx.heading("Gerenciamento do Bot Telegram", class_name="text-2xl font-bold text-foreground"),
        rx.text("Monitoramento em tempo real do bot e análise de uso", class_name="text-base text-muted-foreground"),
        
        # Bot status overview
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("circle", size=16, class_name="text-green-500"),
                        rx.text("Status", class_name="text-sm text-muted-foreground"),
                        class_name="items-center space-x-2",
                    ),
                    rx.text("Online", class_name="text-lg font-bold text-green-500"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Usuários Ativos", class_name="text-sm text-muted-foreground"),
                    rx.text("342", class_name="text-lg font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Mensagens/Hoje", class_name="text-sm text-muted-foreground"),
                    rx.text("1.2K", class_name="text-lg font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Tempo Resposta", class_name="text-sm text-muted-foreground"),
                    rx.text("1.2s", class_name="text-lg font-bold text-foreground"),
                    class_name="space-y-1",
                ),
                class_name="p-4",
            ),
            class_name="grid grid-cols-2 md:grid-cols-4 gap-4 w-full",
        ),
        
        # Control buttons
        rx.hstack(
            rx.button(
                "Reiniciar Bot",
                class_name="bg-yellow-500 text-yellow-900 hover:bg-yellow-600 px-4 py-2 rounded-md text-sm font-medium",
                on_click=GiftCardState.restart_bot,
            ),
            rx.button(
                "Limpar Logs",
                class_name="bg-red-500 text-red-900 hover:bg-red-600 px-4 py-2 rounded-md text-sm font-medium",
                on_click=GiftCardState.clear_logs,
            ),
            rx.button(
                "Exportar Logs",
                class_name="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md text-sm font-medium",
                on_click=rx.download(
                    data="bot_logs",
                    filename="logs_telegram_bot.json"
                ),
            ),
            class_name="items-center space-x-4",
        ),
        
        # Bot metrics charts
        rx.card(
            rx.vstack(
                rx.text("Métricas do Bot", class_name="text-lg font-medium text-foreground"),
                rx.text("Gráficos de uso e performance", class_name="text-sm text-muted-foreground"),
                class_name="space-y-2",
            ),
            class_name="p-4 w-full",
        ),
        
        # Bot commands usage
        rx.card(
            rx.vstack(
                rx.text("Comandos Mais Usados", class_name="text-lg font-medium text-foreground"),
                rx.vstack(
                    rx.hstack(
                        rx.text("/start", class_name="text-sm text-foreground"),
                        rx.spacer(),
                        rx.text("245 vezes", class_name="text-xs text-muted-foreground"),
                        class_name="w-full",
                    ),
                    rx.hstack(
                        rx.text("/comprar", class_name="text-sm text-foreground"),
                        rx.spacer(),
                        rx.text("189 vezes", class_name="text-xs text-muted-foreground"),
                        class_name="w-full",
                    ),
                    rx.hstack(
                        rx.text("/saldo", class_name="text-sm text-foreground"),
                        rx.spacer(),
                        rx.text("156 vezes", class_name="text-xs text-muted-foreground"),
                        class_name="w-full",
                    ),
                    class_name="space-y-2",
                ),
                class_name="space-y-3",
            ),
            class_name="p-4 w-full",
        ),
        
        # Bot logs
        rx.card(
            rx.vstack(
                rx.text("Logs do Bot", class_name="text-lg font-medium text-foreground"),
                rx.text("Últimas atividades do bot", class_name="text-sm text-muted-foreground"),
                rx.text(
                    "2024-01-15 10:30:45 - Bot iniciado\n2024-01-15 10:31:12 - Novo usuário: @usuario123\n2024-01-15 10:32:01 - Compra realizada: R$ 50.00\n2024-01-15 10:33:28 - PIX confirmado",
                    class_name="font-mono text-xs text-foreground whitespace-pre-wrap",
                ),
                class_name="space-y-2",
            ),
            class_name="p-4 w-full",
        ),
        
        class_name="space-y-6 w-full",
    )