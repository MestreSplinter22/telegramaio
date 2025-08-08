"""Bot control buttons component."""

import reflex as rx
from ...backend.giftcard_state import GiftCardState


def bot_controls() -> rx.Component:
    """Bot control buttons."""
    return rx.hstack(
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
    )