"""Authentication state for dashboard login/logout and session management."""

import reflex as rx
from typing import Optional


class AuthState(rx.State):
    """Authentication state for handling login/logout and session."""
    
    # User authentication
    is_logged_in: bool = False
    current_user: Optional[str] = None
    user_role: str = "user"
    
    def login(self, username: str, password: str) -> rx.event:
        """Handle user login."""
        # Implementar lógica de autenticação real
        # Por enquanto, apenas simula login
        self.is_logged_in = True
        self.current_user = username
        return rx.redirect("/dashboard")
    
    def logout(self) -> rx.event:
        """Handle user logout."""
        self.is_logged_in = False
        self.current_user = None
        return rx.redirect("/login")
    
    def check_auth(self) -> bool:
        """Check if user is authenticated."""
        return self.is_logged_in