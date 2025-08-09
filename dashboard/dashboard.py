"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx

from . import styles
from .pages import *
from .backend.models import create_all

# Create the app.
app = rx.App(
    theme=rx.theme(appearance="dark"),
    stylesheets=["/style.css"],
)

# Create all database tables when the app starts
create_all()

app.add_page(
    rx.center(
        rx.text("Tailwind & Reflex!"),
        class_name="bg-background w-full h-[100vh]",
    ),
    "/teste",
)
