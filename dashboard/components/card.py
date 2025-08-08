import reflex as rx

from dashboard import styles


def card(*children, **props):
    """Card component with Tailwind CSS styling using theme variables."""
    return rx.card(
        *children,
        class_name="bg-card text-card-foreground border border-border rounded-lg shadow-lg",
        **props,
    )
