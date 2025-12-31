"""UI state for dashboard sidebar, theme and navigation."""

import reflex as rx


class UIState(rx.State):
    """UI state for handling sidebar, theme and navigation."""
    
    # Sidebar state
    sidebar_collapsed: bool = False
    
    # Theme state
    theme: str = "light"  # "light" or "dark"
    
    # Navigation state
    current_page: str = "/"
    sidebar_items: list = [
        {"name": "Visão Geral", "icon": "home", "route": "/dashboard"},
        {"name": "Transações", "icon": "credit-card", "route": "/transactions"},
        {"name": "Usuários", "icon": "users", "route": "/users"},
        {"name": "Produtos", "icon": "package", "route": "/products"},
        {"name": "Configurações", "icon": "settings", "route": "/settings"},
    ]
    
    def toggle_sidebar(self):
        """Toggle sidebar collapsed state."""
        self.sidebar_collapsed = not self.sidebar_collapsed
    
    def change_theme(self):
        """Toggle between light and dark theme."""
        self.theme = "dark" if self.theme == "light" else "light"
    
    def navigate_to(self, page: str):
        """Navigate to a specific page."""
        self.current_page = page
        return rx.redirect(page)
    
    def get_active_sidebar_item(self):
        """Get the active sidebar item based on current page."""
        for item in self.sidebar_items:
            if item["route"] == self.current_page:
                return item["name"]
        return "Visão Geral"