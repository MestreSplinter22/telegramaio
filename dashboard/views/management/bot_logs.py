"""Bot logs component."""

import reflex as rx
from ...components.ui.card import card
from ...backend.states.bot.bot_state import BotState

def bot_logs() -> rx.Component:
    """Bot activity logs."""
    return card(
        rx.vstack(
            rx.text("Logs do Bot", class_name="text-lg font-medium text-foreground"),
            rx.text("Últimas atividades (Tempo Real)", class_name="text-sm text-muted-foreground"),
            
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        BotState.recent_logs_list,
                        lambda log: rx.text(
                            log,
                            class_name="font-mono text-xs text-foreground whitespace-pre-wrap border-b border-border/50 py-1"
                        )
                    ),
                    class_name="space-y-1",
                ),
                class_name="h-[200px] w-full pr-4", # Altura fixa com scroll
                type="always"
            ),
            class_name="space-y-2",
        ),
        class_name="p-4 w-full",
    )