"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx

from . import styles
from .pages import *

# Create the app.
app = rx.App(
    theme=rx.theme(appearance="dark"),
    stylesheets=["/style.css"],
)
app.add_page(
    rx.center(
        rx.text("Tailwind & Reflex!"),
        class_name="bg-background w-full h-[100vh]",
    ),
    "/teste",
)
