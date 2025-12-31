# dashboard/backend/models/base.py

import reflex as rx
import sqlmodel
from sqlmodel import Field
from sqlalchemy import Column, JSON
from datetime import datetime
from typing import Optional, Dict, Any


class BaseSQLModel(sqlmodel.SQLModel):
    """Classe base para todos os modelos do sistema."""
    pass