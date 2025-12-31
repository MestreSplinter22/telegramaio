"""Media Section Component for Flow Editor"""
import reflex as rx
from dashboard.backend.states.flow_state import FlowState
from .theme import THEME, section_header

def media_section(index: int, block: dict):
    """Renderiza a seção de mídia do bloco."""
    has_image = block.contains("image_url")
    has_video = block.contains("video_url")
    media_type = rx.cond(has_image, "image", rx.cond(has_video, "video", "none"))
    
    return rx.box(
        section_header("image", "Mídia & Anexos"),
        rx.flex(
            rx.select(
                ["none", "image", "video"],
                value=media_type,
                on_change=lambda val: FlowState.set_media_type(index, val),
                size="2", variant="soft", color_scheme="gray",
                width="120px", flex_shrink="0"
            ),
            rx.cond(
                media_type != "none",
                rx.input(
                    value=rx.cond(media_type == "image", block["image_url"], block["video_url"]),
                    placeholder="Cole a URL do arquivo aqui...",
                    on_change=lambda val: FlowState.update_media_url(index, rx.cond(media_type=="image", "image_url", "video_url"), val),
                    variant="soft", color_scheme="gray", size="2", width="100%",
                    bg=THEME["input_bg"]
                )
            ),
            gap="3", width="100%", align="center"
        ),
        padding="16px", width="100%"
    )