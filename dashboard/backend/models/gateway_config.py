# dashboard/backend/models/gateway_config.py

import reflex as rx
from sqlmodel import Field
from sqlalchemy import Column, JSON
from datetime import datetime
from typing import Optional, Dict, Any
from .base import BaseSQLModel


class GatewayConfig(BaseSQLModel, table=True):
    __tablename__ = "gatewayconfig"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # ex: "efi_bank", "mercadopago"
    is_active: bool = False
    is_sandbox: bool = True  # True = Homologação, False = Produção
    
    # Credenciais armazenadas em JSON para flexibilidade
    # Ex: {"client_id": "...", "client_secret": "...", "certificate": "caminho/arquivo.p12"}
    credentials: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Configurações operacionais
    # Ex: {"min_deposit": 50.00, "webhook_url": "https://seu-app.com/api/webhook/efi"}
    config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)