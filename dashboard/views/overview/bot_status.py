"""Bot status card component."""

import reflex as rx


def bot_status_card() -> rx.Component:
    """Bot status monitoring card."""
    return rx.vstack(
        rx.hstack(
            rx.icon("bot", size=20, class_name="text-primary"),
            rx.text("Status do Bot", class_name="text-lg font-medium text-foreground"),
            class_name="items-center space-x-2 justify-center",
        ),
        rx.spacer(),
        rx.vstack(
            rx.hstack(
                rx.icon("circle", size=16, color="green"),
                rx.text("Bot Online", size="3"),
                rx.spacer(),
                rx.text("2ms", size="2", color="gray"),
                class_name="w-full",
            ),
            rx.hstack(
                rx.icon("users", size=16, color="blue"),
                rx.text("Usuários Ativos", size="3"),
                rx.spacer(),
                rx.text("342", size="2", color="gray"),
                class_name="w-full",
            ),
            rx.hstack(
                rx.icon("message-square", size=16, color="purple"),
                rx.text("Mensagens/Hoje", size="3"),
                rx.spacer(),
                rx.text("1.2K", size="2", color="gray"),
                class_name="w-full",
            ),
            rx.hstack(
                rx.icon("command", size=16, color="orange"),
                rx.text("Comandos Executados", size="3"),
                rx.spacer(),
                rx.text("847", size="2", color="gray"),
                class_name="w-full",
            ),
            spacing="4",
            class_name="w-full px-4",
        ),
        rx.spacer(),
        spacing="6",
        class_name="w-full h-full",
    )