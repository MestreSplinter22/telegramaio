"""Bot status cards component."""

import reflex as rx
from ...components.ui.card import card


def bot_status_card(title: str, value: str, status: str = "default") -> rx.Component:
    """Create a single bot status card.
    
    Args:
        title: The card title
        value: The card value
        status: The status color (green, red, yellow, default)
    
    Returns:
        A bot status card component
    """
    status_colors = {
        "green": "text-green-500",
        "red": "text-red-500",
        "yellow": "text-yellow-500",
        "default": "text-foreground"
    }
    
    status_color = status_colors.get(status, "text-foreground")
    
    return card(
        rx.vstack(
            rx.hstack(
                rx.icon("circle", size=16, class_name=status_color) if status != "default" else rx.box(),
                rx.text(title, class_name="text-sm text-muted-foreground"),
                class_name="items-center space-x-2",
            ) if status != "default" else rx.text(title, class_name="text-sm text-muted-foreground"),
            rx.text(value, class_name=f"text-lg font-bold {status_color}"),
            class_name="space-y-1",
        ),
        class_name="p-4",
    )


def bot_status_cards() -> rx.Component:
    """Bot status overview cards."""
    return rx.grid(
        bot_status_card("Status", "Online", "green"),
        bot_status_card("Usuários Ativos", "342", "default"),
        bot_status_card("Mensagens/Hoje", "1.2K", "default"),
        bot_status_card("Tempo Resposta", "1.2s", "default"),
        class_name="grid grid-cols-2 md:grid-cols-4 gap-4 w-full",
    )