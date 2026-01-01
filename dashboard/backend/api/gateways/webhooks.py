"""
Módulo para lidar com webhooks de diferentes gateways
"""
from fastapi import Request
from typing import Optional, Dict, Any
import json
import os
from dashboard.backend.telegram.bot import bot
from dashboard.backend.telegram.common.keyboard_builder import build_keyboard
from dashboard.backend.models import Transaction, User
from .services import TransactionService
from .constants import (
    WEBHOOK_STATUS_PAID_OUT,
    WEBHOOK_STATUS_COMPLETED,
    ERROR_INVALID_JSON,
    ERROR_VALUE_MISMATCH,
    FLOW_FILE_PATH,
    VALUE_TOLERANCE
)
import reflex as rx


class WebhookService:
    """
    Serviço para processar webhooks de diferentes gateways
    """
    
    @staticmethod
    async def process_suitpay_webhook(request: Request) -> Dict[str, Any]:
        """
        Processa webhook da SuitPay
        """
        try:
            data = await request.json()
            print(f"🔔 Webhook SuitPay Recebido: {data}")
        except:
            return {"status": "error", "msg": ERROR_INVALID_JSON}

        # Validação simples de status
        if data.get("statusTransaction") != WEBHOOK_STATUS_PAID_OUT:
            return {"status": "ignored", "reason": "Not PAID_OUT"}

        request_number = data.get("requestNumber")
        
        # Busca transação pendente compatível
        txn = None
        
        # Filtra transações pendentes para otimizar
        with rx.session() as session:
            txns = session.query(Transaction).filter(Transaction.status == "pending").all()
            
            for t in txns:
                # Verifica se o ID da requisição está nos metadados
                if t.extra_data and (request_number in t.extra_data):
                    txn = t
                    break
            
            if txn:
                # Valida valor (evita fraudes de pagar R$ 0,01 para recarga de R$ 100)
                valor_pago = float(data.get("value", 0))
                if abs(txn.amount - valor_pago) > VALUE_TOLERANCE:
                    print(f"❌ Fraude Detectada: Valor esperado {txn.amount}, pago {valor_pago}")
                    return {"status": "error", "msg": ERROR_VALUE_MISMATCH}

                # Confirma Pagamento
                txn.status = "completed"
                session.add(txn)
                
                # Credita Saldo ao Usuário
                user = session.query(User).filter(User.telegram_id == txn.user_id).first()
                if user:
                    user.balance += txn.amount
                    user.total_spent += txn.amount  # Opcional: ajustar lógica contábil
                    session.add(user)
                    
                    # Notifica via Bot
                    try:
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=f"✅ <b>Pagamento Confirmado!</b>\n\n💰 Crédito de R$ {txn.amount:.2f} adicionado à sua conta.",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        print(f"Erro ao notificar Telegram: {e}")
                
                session.commit()
                print(f"✅ Transação {txn.id} liquidada com sucesso.")
                return {"response": "OK"}
                
        print(f"⚠️ Transação não encontrada para requestNumber: {request_number}")
        return {"status": "not_found"}

    @staticmethod
    async def process_openpix_webhook(request: Request) -> Dict[str, Any]:
        """
        Processa webhook da OpenPix
        """
        try:
            data = await request.json()
        except:
            return {"status": "error", "msg": ERROR_INVALID_JSON}

        event_type = data.get("event", "")
        charge_data = data.get("charge", {})
        
        if "COMPLETED" not in event_type and charge_data.get("status") != "COMPLETED":
            return {"status": "ignored"}

        txid = charge_data.get("correlationID") or data.get("correlationID")
        if not txid:
            return {"status": "error", "msg": "No correlationID found"}

        print(f"🔔 [Webhooks] Webhook OpenPix Confirmado: {txid}")

        # Completar transação
        
        with rx.session() as session:
            txn = session.query(Transaction).filter(
                Transaction.status == "pending",
                Transaction.extra_data.contains(txid)
            ).first()

            if txn:
                valor_pago = float(charge_data.get("value", 0))
                if valor_pago > (txn.amount * 10): 
                    valor_pago = valor_pago / 100

                if abs(txn.amount - valor_pago) > VALUE_TOLERANCE:
                    return {"status": "error", "msg": ERROR_VALUE_MISMATCH}

                txn.status = "completed"
                user = session.query(User).filter(User.telegram_id == txn.user_id).first()
                if user:
                    user.balance += txn.amount
                    user.total_spent += txn.amount
                    session.add(user)
                    
                    # --- LÓGICA DE MENSAGEM PERSONALIZADA (CORRIGIDA COM BOTÕES) ---
                    custom_message_sent = False
                    
                    try:
                        print(f"🔍 [Webhooks] Processando mensagem personalizada para TXID: {txid}")
                        
                        # 1. Carregar o fluxo para consultar os nós
                        if os.path.exists(FLOW_FILE_PATH):
                            with open(FLOW_FILE_PATH, "r", encoding="utf-8") as f:
                                flow_data = json.load(f)
                            screens = flow_data.get("screens", {})
                            
                            # 2. Identificar qual era a tela de pagamento
                            payment_screen_id = None
                            try:
                                extra_data = json.loads(txn.extra_data) if txn.extra_data else {}
                                payment_screen_id = extra_data.get("screen_id")
                            except Exception as e:
                                print(f"❌ Erro ao parsear extra_data: {e}")
                                pass
                            
                            # 3. Se encontrou o nó de pagamento, verificar se tem webhook
                            if payment_screen_id and payment_screen_id in screens:
                                payment_node = screens[payment_screen_id]
                                target_node_id = payment_node.get("webhook")
                                print(f"🔗 Webhook aponta para: {target_node_id}")
                                
                                # 4. Se tem nó de sucesso, buscar a mensagem
                                if target_node_id and target_node_id in screens:
                                    success_node = screens[target_node_id]
                                    message_text = success_node.get("text", "")
                                    
                                    if message_text:
                                        # Formatar texto
                                        formatted_text = message_text.replace("{amount}", f"{txn.amount:.2f}")\
                                                                     .replace("{txid}", txid)
                                        
                                        # Construir Teclado
                                        markup = None
                                        if "buttons" in success_node and success_node["buttons"]:
                                            try:
                                                print(f"🔘 [Webhooks] Criando botões: {success_node['buttons']}")
                                                markup = build_keyboard(success_node["buttons"])
                                            except Exception as kb_err:
                                                print(f"❌ Erro ao criar teclado: {kb_err}")

                                        # Enviar com reply_markup
                                        await bot.send_message(
                                            chat_id=user.telegram_id,
                                            text=formatted_text,
                                            parse_mode="Markdown",
                                            reply_markup=markup
                                        )
                                        custom_message_sent = True
                                        print(f"✅ [Webhooks] Mensagem (com botões) enviada!")
                                    else:
                                        print(f"⚠️ Texto vazio no nó {target_node_id}")
                                else:
                                    print(f"⚠️ Nó de sucesso não encontrado")
                            else:
                                print(f"⚠️ Nó de pagamento não encontrado")
                    except Exception as e:
                        print(f"❌ Erro ao processar mensagem personalizada: {e}")
                    
                    # Fallback
                    if not custom_message_sent:
                        print("🔄 Usando mensagem padrão como fallback")
                        try:
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=f"✅ <b>Pagamento Confirmado!</b>\n\n💰 + R$ {txn.amount:.2f}",
                                parse_mode="HTML"
                            )
                        except Exception as e:
                            print(f"❌ Erro ao enviar mensagem padrão: {e}")
                
                session.commit()
                return {"status": "ok"}
        
        return {"status": "not_found"}


class EfiWebhookService:
    """
    Serviço para processar webhook da Efí (mantido para compatibilidade futura)
    """
    
    @staticmethod
    async def process_efi_webhook(request: Request) -> Dict[str, Any]:
        """
        Processa webhook da Efí
        """
        # (Mantendo o endpoint para caso você use Efí no futuro)
        # ... código do webhook da Efí se necessário ...
        return {"status": "ok"}