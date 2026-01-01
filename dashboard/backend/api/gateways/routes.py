# dashboard/backend/api/gateways/routes.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import reflex as rx
import json

# Imports do Sistema
from dashboard.backend.models import GatewayConfig, Transaction, User
from dashboard.backend.telegram.bot import bot

# Imports do módulo de gateways
from .constants import (
    GATEWAY_NAME_EFI,
    GATEWAY_NAME_SUITPAY,
    GATEWAY_NAME_OPENPIX,
    FLOW_FILE_PATH
)
from .services import PaymentService
from .webhooks import WebhookService, EfiWebhookService
from .exceptions import (
    GatewayNotActiveException,
    UserNotFoundException,
    PaymentCreationException,
    ValueMismatchException
)

router = APIRouter(prefix="/api/payment", tags=["payment"])

class PaymentRequest(BaseModel):
    user_telegram_id: str
    amount: float
    gateway_name: str = "suitpay"
    screen_id: Optional[str] = None  # Adicionado para suportar fluxos personalizados

class PaymentResponse(BaseModel):
    txid: str
    pix_copia_cola: str
    qrcode_base64: str
    status: str

@router.post("/create", response_model=PaymentResponse)
async def create_payment(data: PaymentRequest):
    """
    Cria uma cobrança PIX imediata na Gateway selecionada (Efí ou SuitPay).
    """
    try:
        result = PaymentService.create_payment(
            user_telegram_id=data.user_telegram_id,
            amount=data.amount,
            gateway_name=data.gateway_name,
            screen_id=data.screen_id
        )
        return result
    except GatewayNotActiveException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except PaymentCreationException as e:
        print(f"Erro ao criar pagamento: {e}")
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        print(f"Erro inesperado ao criar pagamento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar pagamento")

# --- WEBHOOK SUITPAY ---
@router.post("/webhook/suitpay")
async def suitpay_webhook(request: Request):
    """
    Recebe notificação da SuitPay e confirma pagamento.
    """
    return await WebhookService.process_suitpay_webhook(request)

# --- WEBHOOK EFI (MANTIDO) ---
@router.post("/webhook/efi")
async def efi_webhook(request: Request):
    # (Mantendo o endpoint para caso você use Efí no futuro)
    return await EfiWebhookService.process_efi_webhook(request)


# --- NOVO WEBHOOK OPENPIX ---
@router.post("/webhook/openpix")
async def openpix_webhook(request: Request):
    return await WebhookService.process_openpix_webhook(request)

def register_payment_routes(app):
    app.include_router(router)