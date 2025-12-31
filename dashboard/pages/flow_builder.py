import reflex as rx
from dashboard.components.ui.template.navbar import navbar
from dashboard.components.ui.template.sidebar import sidebar
from dashboard.backend.states.flow_state import FlowState

# Importar os componentes dos painéis
from dashboard.components.flow_builder.canvas_panel import canvas_panel
from dashboard.components.flow_builder.editor_panel import editor_panel
from dashboard.components.flow_builder.styles import THEME

@rx.page(route="/flows", title="Bot Flow Builder")
def flow_builder_page() -> rx.Component:
    return rx.box(
        rx.flex(
            sidebar(),
            rx.box(
                navbar(),
                rx.box(
                    rx.grid(
                        canvas_panel(),
                        editor_panel(),
                        columns="2fr 1fr",
                        gap="4",
                        width="100%",
                        height="85vh"
                    ),
                    padding="24px", 
                    width="100%", 
                    min_height="100vh", 
                    bg=THEME["app_bg"]
                ),
                width="100%", display="flex", flex_direction="column",
            ),
            width="100%", display="flex",
        ),
        on_mount=FlowState.load_flow
    )