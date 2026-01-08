"""User management state."""

import reflex as rx
from sqlmodel import select, or_
from typing import List, Optional
# Importando o modelo ORM correto (subindo 3 níveis: states/users -> states -> backend -> models)
from ...models import User


class UserState(rx.State):
    """User management state."""
    
    # User data
    users: List[User] = []
    users_loading: bool = False
    
    # Selected user for details
    selected_user: Optional[User] = None
    
    # Filters
    user_search: str = ""
    user_status_filter: str = "all"
    
    def load_users(self):
        """Load users from database."""
        self.users_loading = True
        try:
            with rx.session() as session:
                # Busca usuários ordenados por criação (mais recentes primeiro)
                query = select(User).order_by(User.created_at.desc())
                self.users = session.exec(query).all()
        except Exception as e:
            print(f"Erro ao carregar usuários: {e}")
        finally:
            self.users_loading = False
    
    @rx.var
    def filtered_users(self) -> List[User]:
        """Get filtered users based on search and status."""
        filtered = self.users
        
        # Filtro de Busca (Nome ou Username ou ID Telegram)
        if self.user_search:
            search_lower = self.user_search.lower()
            filtered = [
                user for user in filtered
                if (
                    search_lower in (user.first_name or "").lower() or
                    search_lower in (user.last_name or "").lower() or
                    search_lower in (user.username or "").lower() or
                    search_lower in user.telegram_id
                )
            ]
        
        # Filtro de Status
        if self.user_status_filter != "all":
            filtered = [
                user for user in filtered
                if user.status == self.user_status_filter
            ]
        
        return filtered
    
    def set_selected_user(self, user: User):
        """Set selected user for details view."""
        self.selected_user = user
    
    def clear_selected_user(self):
        """Clear selected user."""
        self.selected_user = None
    
    def set_user_search(self, value: str):
        """Set user search query."""
        self.user_search = value

    def set_user_status_filter(self, value: str):
        """Set user status filter."""
        self.user_status_filter = value

    def update_user_status(self, user_id: int, new_status: str):
        """Update user status in database."""
        with rx.session() as session:
            user = session.get(User, user_id)
            if user:
                user.status = new_status
                session.add(user)
                session.commit()
                session.refresh(user)
                
                # Recarrega a lista para atualizar a UI
                self.load_users()
                return rx.toast.success(f"Status do usuário atualizado para {new_status}")
            else:
                return rx.toast.error("Usuário não encontrado")