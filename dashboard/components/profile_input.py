import reflex as rx


def profile_input(
    label: str,
    name: str,
    placeholder: str,
    type: str,
    icon: str,
    default_value: str = "",
) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(icon, size=16, stroke_width=1.5, class_name="text-muted-foreground"),
            rx.text(label, class_name="text-sm font-medium text-foreground"),
            class_name="w-full items-center space-x-2",
        ),
        rx.input(
            placeholder=placeholder,
            type=type,
            default_value=default_value,
            class_name="w-full bg-background border border-input rounded-md px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
            name=name,
        ),
        class_name="flex flex-col space-y-1 w-full",
    )
