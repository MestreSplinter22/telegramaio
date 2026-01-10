"""Bot metrics component."""

import reflex as rx
from ...components.ui.card import card
from ...backend.states.bot.bot_state import BotState


def bot_metrics() -> rx.Component:
    """Bot metrics charts card."""
    return card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Métricas de Performance", class_name="text-lg font-medium text-foreground"),
                    rx.text("Volume e Distribuição de Interações", class_name="text-sm text-muted-foreground"),
                ),
                rx.spacer(),
                # Botãozinho de refresh manual opcional
                rx.icon_button(
                    rx.icon("refresh-cw"),
                    on_click=BotState.get_bot_status,
                    variant="ghost",
                    size="2"
                ),
                class_name="w-full items-start"
            ),
            
            rx.grid(
                # --- GRÁFICO 1: Volume por Hora (Area Chart) ---
                rx.vstack(
                    rx.text("Atividade (24h)", class_name="text-xs font-semibold mb-2"),
                    rx.recharts.area_chart(
                        rx.recharts.area(
                            data_key="count",
                            stroke="#8884d8",
                            fill="#8884d8",
                            name="Interações"
                        ),
                        rx.recharts.x_axis(data_key="time", font_size=10),
                        rx.recharts.y_axis(font_size=10),
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                        rx.recharts.tooltip(),
                        data=BotState.interactions_chart_data,
                        height=200,
                        width="100%",
                    ),
                    class_name="w-full p-2 border rounded-lg bg-card/50",
                ),

                # --- GRÁFICO 2: Distribuição de Tipos (Pie Chart) ---
                rx.vstack(
                    rx.text("Tipos de Interação", class_name="text-xs font-semibold mb-2"),
                    rx.center(
                        rx.recharts.pie_chart(
                            rx.recharts.pie(
                                data=BotState.interaction_types_data,
                                data_key="value",
                                name_key="name",
                                cx="50%",
                                cy="50%",
                                outer_radius=60,
                                label=True,
                            ),
                            rx.recharts.legend(),
                            rx.recharts.tooltip(),
                            height=200,
                            width="100%",
                        ),
                        class_name="w-full"
                    ),
                    class_name="w-full p-2 border rounded-lg bg-card/50",
                ),
                
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-4 w-full mt-4"
            ),
            class_name="space-y-2 w-full",
        ),
        class_name="p-4 w-full",
    )