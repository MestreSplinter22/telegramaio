"""Transaction management state."""

import reflex as rx
from sqlmodel import select
from typing import List, Optional
from datetime import datetime
# Importando do módulo de modelos do backend (ORM), subindo 3 níveis
from ...models import Transaction

class TransactionState(rx.State):
    """Transaction management state."""
    
    # Transaction data - usando o modelo do ORM
    transactions: List[Transaction] = []
    transactions_loading: bool = False
    
    # Filters
    transaction_type_filter: str = "all"
    transaction_status_filter: str = "all"
    transaction_date_filter: str = "all"
    transaction_search: str = ""
    
    # Selected transaction
    selected_transaction: Optional[Transaction] = None
    
    def load_transactions(self):
        """Load transactions from database."""
        self.transactions_loading = True
        try:
            with rx.session() as session:
                # Busca ordenada por timestamp decrescente
                statement = select(Transaction).order_by(Transaction.timestamp.desc())
                self.transactions = session.exec(statement).all()
        except Exception as e:
            print(f"Erro ao carregar transações: {e}")
        finally:
            self.transactions_loading = False
    
    def get_filtered_transactions(self) -> List[Transaction]:
        """Get filtered transactions."""
        filtered = self.transactions
        
        # Filtro por Tipo
        if self.transaction_type_filter != "all":
            filtered = [txn for txn in filtered if txn.type == self.transaction_type_filter]
        
        # Filtro por Status
        if self.transaction_status_filter != "all":
            filtered = [txn for txn in filtered if txn.status == self.transaction_status_filter]
        
        # Filtro de Busca (Search)
        if self.transaction_search:
            search_lower = self.transaction_search.lower()
            filtered = [
                txn for txn in filtered
                if (
                    (txn.description and search_lower in txn.description.lower()) or
                    (txn.id is not None and search_lower in str(txn.id))
                )
            ]
        
        return filtered
    
    @rx.var
    def filtered_transactions(self) -> List[Transaction]:
        """Get filtered transactions for current view."""
        return self.get_filtered_transactions()
    
    # --- Variáveis Computadas para os Cards ---

    @rx.var
    def total_transactions_completed(self) -> int:
        """Contagem apenas das transações com status 'completed'."""
        return len([txn for txn in self.transactions if txn.status == "completed"])

    @rx.var
    def total_revenue_completed(self) -> float:
        """Soma do valor (amount) apenas das transações 'completed'."""
        return sum(txn.amount for txn in self.transactions if txn.status == "completed")

    @rx.var
    def total_rows_count(self) -> int:
        """Contagem total de todas as linhas (rows) na tabela."""
        return len(self.transactions)
    
    # --- Ações de UI ---

    def set_selected_transaction(self, transaction: Transaction):
        self.selected_transaction = transaction
    
    def clear_selected_transaction(self):
        self.selected_transaction = None
    
    def set_transaction_search(self, value: str):
        self.transaction_search = value

    def set_transaction_type_filter(self, value: str):
        self.transaction_type_filter = value

    def set_status_filter(self, value: str):
        self.transaction_status_filter = value

    def set_date_range(self, value: str):
        self.transaction_date_filter = value

    def update_transaction_status(self, transaction_id: int, new_status: str):
        """Update transaction status in DB."""
        with rx.session() as session:
            txn = session.get(Transaction, transaction_id)
            if txn:
                txn.status = new_status
                session.add(txn)
                session.commit()
                session.refresh(txn)
                self.load_transactions()
                return rx.toast.success(f"Status atualizado para {new_status}")
            else:
                return rx.toast.error("Transação não encontrada")