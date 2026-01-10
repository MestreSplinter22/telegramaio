"""Bot status card component."""

import reflex as rx
from ...backend.states.bot.bot_state import BotState

def bot_status_card() -> rx.Component:
    """Bot status monitoring card."""
    # Chama o load data quando o componente monta (opcional, ou usar on_load na página)
    return rx.vstack(
        # Header
        rx.hstack(
            rx.icon("bot", size=22, style={"color": "var(--icon)"}),
            rx.text("Status do Bot", class_name="text-xl font-semibold text-foreground"),
            class_name="justify-center items-center gap-2",
        ),
        rx.box(class_name="border-b border-border w-full my-2"),

        # Monitoring items list
        rx.box(
            rx.vstack(
                # Bot Status
                rx.hstack(
                    rx.vstack(
                        rx.text("Status do Sistema", class_name="text-sm font-medium text-foreground"),
                        rx.cond(
                            BotState.bot_running,
                            rx.text("Ativo Recentemente", class_name="text-xs text-green-500"),
                            rx.text("Inativo / Ocioso", class_name="text-xs text-muted-foreground"),
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.cond(
                            BotState.bot_running,
                            rx.icon("circle", size=12, class_name="text-green-500"),
                            rx.icon("circle", size=12, class_name="text-gray-500"),
                        ),
                        rx.text(BotState.bot_response_time, class_name="text-xs text-muted-foreground"),
                        spacing="1",
                        align_items="center",
                    ),
                    class_name="w-full items-center py-2",
                ),
                
                # Active Users
                rx.hstack(
                    rx.vstack(
                        rx.text("Usuários Ativos (24h)", class_name="text-sm font-medium text-foreground"),
                        rx.text("Total de interações únicas", class_name="text-xs text-muted-foreground"),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.text(BotState.active_users_count, class_name="text-base font-medium text-foreground"),
                    class_name="w-full items-center py-2",
                ),
                
                # Messages Today
                rx.hstack(
                    rx.vstack(
                        rx.text("Interações Hoje", class_name="text-sm font-medium text-foreground"),
                        rx.text("Mensagens e cliques", class_name="text-xs text-muted-foreground"),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.text(BotState.messages_today_count, class_name="text-base font-medium text-foreground"),
                    class_name="w-full items-center py-2",
                ),
                
                # Commands Executed
                rx.hstack(
                    rx.vstack(
                        rx.text("Comandos Hoje", class_name="text-sm font-medium text-foreground"),
                        rx.text("Ex: /start, /comprar", class_name="text-xs text-muted-foreground"),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.text(BotState.commands_executed_count, class_name="text-base font-medium text-foreground"),
                    class_name="w-full items-center py-2",
                ),
                
                spacing="0",
                class_name="divide-y divide-border w-full",
            ),
            class_name="w-full",
        ),
        spacing="3",
        class_name="w-full h-full p-4 md:p-6",
    )