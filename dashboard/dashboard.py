"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx
from fastapi import FastAPI

from . import styles
from .pages import *
from .backend.models import create_all
from .backend.api import register_all_routes

# Criar uma instância FastAPI para o api_transformer
fastapi_app = FastAPI(title="TelegramaIO API")

# Register all API routes centrally
register_all_routes(fastapi_app)

# Create the app.
app = rx.App(
    theme=rx.theme(appearance="dark"),
    stylesheets=["/style.css"],
    api_transformer=fastapi_app,
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
