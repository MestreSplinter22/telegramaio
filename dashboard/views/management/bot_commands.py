"""Bot commands usage component."""

import reflex as rx
from ...components.ui.card import card
from ...backend.states.bot.bot_state import BotState

def bot_commands() -> rx.Component:
    """Most used bot commands."""
    return card(
        rx.vstack(
            rx.text("Comandos Mais Usados", class_name="text-lg font-medium text-foreground"),
            
            # Lista dinâmica usando rx.foreach
            rx.foreach(
                BotState.top_commands_list,
                lambda item: rx.hstack(
                    rx.text(item["cmd"], class_name="text-sm text-foreground"),
                    rx.spacer(),
                    rx.text(
                        f"{item['count']} vezes", 
                        class_name="text-xs text-muted-foreground"
                    ),
                    class_name="w-full",
                ),
            ),
            
            # Caso a lista esteja vazia
            rx.cond(
                BotState.top_commands_list.length() == 0,
                rx.text("Nenhum comando registrado ainda.", class_name="text-xs text-muted-foreground")
            ),
            
            class_name="space-y-3",
        ),
        class_name="p-4 w-full",
    )