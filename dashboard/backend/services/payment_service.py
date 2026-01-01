# dashboard/backend/services/payment_service.py

import json
import uuid
from typing import Dict, Any, Optional

import reflex as rx
from aiogram.types import BufferedInputFile

from dashboard.backend.models import GatewayConfig, User, Transaction
from dashboard.backend.gateways.efi_service import EfiPixService
from dashboard.backend.gateways.suitpay_service import SuitPayService
from dashboard.backend.gateways.openpix_service import OpenPixService


class PaymentService:
    def __init__(self):
        pass

    def get_active_gateway(self, gateway_name_preferida: Optional[str] = None):
        """Obtém o gateway ativo, com preferência por um gateway específico se informado."""
        with rx.session() as session:
            query = session.query(GatewayConfig).filter(GatewayConfig.is_active == True)
            
            if gateway_name_preferida:
                gateway = query.filter(GatewayConfig.name == gateway_name_preferida).first()
                if gateway:
                    return gateway
            
            # Se não encontrar o gateway preferido ou não foi especificado, pega o primeiro ativo
            gateway = query.first()
            if not gateway:
                gateway = session.query(GatewayConfig).filter(GatewayConfig.is_active == True).first()
            
            return gateway

    def get_or_create_user(self, telegram_id: str, first_name: str, username: Optional[str] = None):
        """Obtém um usuário existente ou cria um novo."""
        with rx.session() as session:
            user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            
            if not user:
                user = User(
                    telegram_id=str(telegram_id),
                    username=username or "SemUser",
                    first_name=first_name,
                    last_name=""
                )
                session.add(user)
                session.commit()
            
            return user

    def create_transaction(self, user_id: str, amount: float, gateway_name: str, 
                          pix_data: Dict[str, Any], success_screen_id: Optional[str] = None, 
                          payment_screen_id: Optional[str] = None):
        """Cria uma transação no banco de dados."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"📝 Criando transação - payment_screen_id: {payment_screen_id}")
        """Cria uma transação no banco de dados."""
        with rx.session() as session:
            extra_data_payload = {
                "txid": pix_data.get("txid"), 
                "gateway_id": pix_data.get("gateway_id"), 
                "external_id": pix_data.get("external_id")
            }
            
            if success_screen_id:
                extra_data_payload["success_screen_id"] = success_screen_id
            
            if payment_screen_id:
                extra_data_payload["screen_id"] = payment_screen_id
                logger.info(f"💾 Salvando screen_id {payment_screen_id} nos metadados")
            else:
                logger.warning("⚠️ payment_screen_id não foi fornecido!")

            logger.info(f"📦 Payload extra_data: {extra_data_payload}")
            
            new_txn = Transaction(
                user_id=user_id,
                type="deposit",
                amount=amount,
                description=f"Recarga via {gateway_name}",
                status="pending",
                extra_data=json.dumps(extra_data_payload)
            )
            session.add(new_txn)
            session.commit()
            
            return new_txn

    def process_payment(self, amount: float, gateway_name: Optional[str], 
                       user_context: Dict[str, Any], success_screen_id: Optional[str] = None,
                       payment_screen_id: Optional[str] = None) -> Dict[str, Any]:
        """Processa um pagamento, gerenciando gateway, usuário e transação."""
        # 1. Busca Gateway
        gateway = self.get_active_gateway(gateway_name)
        if not gateway:
            return {"success": False, "error": "Nenhuma gateway ativa."}

        # 2. Obtém ou cria usuário
        user = self.get_or_create_user(
            telegram_id=user_context["id"],
            first_name=user_context["name"],
            username=user_context.get("username")
        )

        # 3. Gera PIX
        txid = uuid.uuid4().hex
        pix_data = self.generate_pix(gateway, txid, user_context["name"], amount)
        
        if not pix_data or "error" in pix_data:
            return {"success": False, "error": pix_data.get("error", "Erro ao gerar PIX.")}

        # 4. Salva Transação
        transaction = self.create_transaction(
            user_id=user.telegram_id,
            amount=amount,
            gateway_name=gateway.name,
            pix_data={
                "txid": txid,
                "gateway_id": gateway.id,
                "external_id": pix_data.get("external_id")
            },
            success_screen_id=success_screen_id,
            payment_screen_id=payment_screen_id
        )

        return {
            "success": True,
            "pix_data": pix_data,
            "user": user,
            "transaction": transaction
        }

    def generate_pix(self, gateway: GatewayConfig, txid: str, nome_pagador: str, amount: float) -> Dict[str, Any]:
        """Gera um pagamento PIX usando o gateway apropriado."""
        nome_pagador = nome_pagador or "Cliente"
        amount_str = f"{amount:.2f}"
        
        try:
            if gateway.name == "efi_bank":
                service = EfiPixService(gateway)
                efi_resp = service.create_immediate_charge(
                    txid=txid,
                    cpf="12345678909" if gateway.is_sandbox else "00000000000",
                    nome=nome_pagador,
                    valor=amount_str
                )
                return {
                    "pix_copia_cola": efi_resp.get("qrcode") or efi_resp.get("pixCopiaECola"),
                    "qrcode_base64": efi_resp.get("imagemQrcode"),
                    "external_id": txid
                }
                
            elif gateway.name == "suitpay":
                service = SuitPayService(gateway)
                suit_resp = service.create_pix_payment(
                    txid=txid,
                    cpf="00000000000",
                    nome=nome_pagador,
                    email="cliente@email.com",
                    valor=amount
                )
                return {
                    "pix_copia_cola": suit_resp.get("pix_copia_cola"),
                    "qrcode_base64": suit_resp.get("qrcode_base64"),
                    "external_id": suit_resp.get("txid")
                }

            elif gateway.name == "openpix":
                service = OpenPixService(gateway)
                op_resp = service.create_charge(
                    txid=txid,
                    nome=nome_pagador,
                    cpf=None, 
                    valor=amount,
                    email="cliente@sememail.com"
                )
                return {
                    "pix_copia_cola": op_resp.get("pix_copia_cola"),
                    "qrcode_base64": op_resp.get("qrcode_base64"),
                    "external_id": op_resp.get("txid")
                }
            
            return {"error": f"Gateway não suportado: {gateway.name}"}
        except Exception as e:
            return {"error": f"Erro ao gerar PIX com {gateway.name}: {str(e)}"}