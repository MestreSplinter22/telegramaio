"""Bot status card component."""

import reflex as rx


def bot_status_card() -> rx.Component:
    """Bot status monitoring card."""
    return rx.vstack(
        rx.text("Status do Bot", size="4", weight="medium"),
        rx.vstack(
            rx.hstack(
                rx.icon("circle", size=16, color="green"),
                rx.text("Bot Online", size="3"),
                rx.spacer(),
                rx.text("2ms", size="2", color="gray"),
                width="100%",
            ),
            rx.hstack(
                rx.icon("users", size=16, color="blue"),
                rx.text("Usuários Ativos", size="3"),
                rx.spacer(),
                rx.text("342", size="2", color="gray"),
                width="100%",
            ),
            rx.hstack(
                rx.icon("message-square", size=16, color="purple"),
                rx.text("Mensagens/Hoje", size="3"),
                rx.spacer(),
                rx.text("1.2K", size="2", color="gray"),
                width="100%",
            ),
            rx.hstack(
                rx.icon("command", size=16, color="orange"),
                rx.text("Comandos Executados", size="3"),
                rx.spacer(),
                rx.text("847", size="2", color="gray"),
                width="100%",
            ),
            spacing="3",
        ),
        spacing="4",
        width="100%",
    )