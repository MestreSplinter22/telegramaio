"""Revenue chart component for gift card dashboard."""

import reflex as rx
from ...backend.states.dashboard import DashboardState


def revenue_chart() -> rx.Component:
    """Revenue chart showing daily performance."""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.icon("trending-up", size=22, style={"color": "var(--icon-tertiary)"}),
            rx.text("Receita (Últimos 7 dias)", class_name="text-xl font-semibold text-foreground"),
            class_name="justify-center items-center gap-2",
        ),
        rx.box(class_name="border-b border-border w-full my-2"),

        # Chart container
        rx.box(
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="revenue",
                    stroke=rx.color("green", 9),
                    stroke_width=2,
                    dot=True,
                    name="Receita",
                ),
                rx.recharts.x_axis(
                    data_key="day",
                    stroke=rx.color("gray", 8),
                    font_size=12,
                ),
                rx.recharts.y_axis(
                    stroke=rx.color("gray", 8),
                    font_size=12,
                    # Formatador simples, já que o Recharts no Reflex tem limitações com funções lambda aqui
                ),
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3",
                    stroke=rx.color("gray", 5),
                ),
                rx.recharts.tooltip(
                    content_style={
                        "backgroundColor": "#1a1a1a",
                        "borderRadius": "8px",
                        "border": "1px solid #333",
                        "color": "#fff"
                    },
                    item_style={"color": "#fff"}
                ),
                # VINCULANDO AOS DADOS DINÂMICOS
                data=DashboardState.revenue_chart_data,
                width="100%",
                height=300,
            ),
            class_name="w-full max-w-3xl mx-auto",
        ),
        spacing="3",
        class_name="w-full h-full p-4 md:p-6",
    )