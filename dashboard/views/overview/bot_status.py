"""Bot status card component."""

import reflex as rx


def bot_status_card() -> rx.Component:
    """Bot status monitoring card."""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.icon("bot", size=22, class_name="text-primary"),
            rx.text("Status do Bot", class_name="text-xl font-semibold text-foreground"),
            class_name="justify-center items-center gap-2",
        ),
        rx.box(class_name="border-b border-border w-full my-2"),

        # Content (centered within available space)
        rx.box(
            rx.grid(
                rx.box(
                    rx.hstack(
                        rx.icon("circle", size=16, class_name="text-green-500"),
                        rx.text("Bot Online", class_name="text-sm text-foreground"),
                        rx.spacer(),
                        rx.text("2ms", class_name="text-xs text-muted-foreground"),
                        class_name="w-full items-center",
                    ),
                    class_name="w-full rounded-md px-3 py-2 border border-border",
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("users", size=16, class_name="text-blue-500"),
                        rx.text("Usuários Ativos", class_name="text-sm text-foreground"),
                        rx.spacer(),
                        rx.text("342", class_name="text-base font-medium text-foreground"),
                        class_name="w-full items-center",
                    ),
                    class_name="w-full rounded-md px-3 py-2 border border-border",
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("message-square", size=16, class_name="text-purple-500"),
                        rx.text("Mensagens/Hoje", class_name="text-sm text-foreground"),
                        rx.spacer(),
                        rx.text("1.2K", class_name="text-base font-medium text-foreground"),
                        class_name="w-full items-center",
                    ),
                    class_name="w-full rounded-md px-3 py-2 border border-border",
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("command", size=16, class_name="text-orange-500"),
                        rx.text("Comandos Executados", class_name="text-sm text-foreground"),
                        rx.spacer(),
                        rx.text("847", class_name="text-base font-medium text-foreground"),
                        class_name="w-full items-center",
                    ),
                    class_name="w-full rounded-md px-3 py-2 border border-border",
                ),
                class_name="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl mx-auto",
            ),
            class_name="flex-1 flex items-center w-full",
        ),
        spacing="3",
        class_name="w-full h-full p-4 md:p-6",
    )