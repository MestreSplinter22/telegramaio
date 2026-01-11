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
                if t.extra_data and (str(request_number) in t.extra_data):
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
        Processa webhook da OpenPix com suporte a mensagens customizadas do remarketing
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
                    
                    custom_message_sent = False
                    
                    # --- PRIORIDADE 1: DADOS DE REMARKETING (remarketing_success_data) ---
                    try:
                        extra_data = json.loads(txn.extra_data) if txn.extra_data else {}
                        success_screen_id = extra_data.get("success_screen_id")
                        remarketing_data = extra_data.get("remarketing_success_data")
                        
                        # Se existe success_screen_id = "remarketing_success" E dados customizados
                        if success_screen_id == "remarketing_success" and remarketing_data:
                            print(f"✨ [Webhooks] Detectado pagamento de REMARKETING com dados customizados para {txid}")
                            
                            # Extrair dados
                            text = remarketing_data.get("text", "🎉 Pagamento Confirmado!")
                            image_url = remarketing_data.get("image_url", "")
                            video_url = remarketing_data.get("video_url", "")
                            buttons_data = remarketing_data.get("buttons", [])
                            
                            # Formatar texto
                            formatted_text = text.replace("{amount}", f"{txn.amount:.2f}") \
                                                .replace("{txid}", txid) \
                                                .replace("{first_name}", user.first_name)
                            
                            # Construir teclado se houver botões
                            markup = None
                            if buttons_data:
                                try:
                                    markup = build_keyboard(buttons_data)
                                    print(f"🔘 [Webhooks] Teclado criado com {len(buttons_data)} linha(s)")
                                except Exception as kb_err:
                                    print(f"❌ Erro ao criar teclado: {kb_err}")
                            
                            # Enviar mídia apropriada
                            if video_url:
                                await bot.send_video(
                                    chat_id=user.telegram_id,
                                    video=video_url,
                                    caption=formatted_text,
                                    parse_mode="HTML",
                                    reply_markup=markup
                                )
                            elif image_url:
                                await bot.send_photo(
                                    chat_id=user.telegram_id,
                                    photo=image_url,
                                    caption=formatted_text,
                                    parse_mode="HTML",
                                    reply_markup=markup
                                )
                            else:
                                await bot.send_message(
                                    chat_id=user.telegram_id,
                                    text=formatted_text,
                                    parse_mode="HTML",
                                    reply_markup=markup
                                )
                            
                            custom_message_sent = True
                            print("✅ [Webhooks] Mensagem de remarketing customizada enviada!")
                            
                    except Exception as e_remarketing:
                        print(f"❌ Erro ao processar remarketing: {e_remarketing}")
                    
                    # --- PRIORIDADE 2: ARQUIVO DE FLUXO (para fluxos normais) ---
                    if not custom_message_sent:
                        try:
                            print(f"🔍 [Webhooks] Tentando buscar fluxo no arquivo para TXID: {txid}")
                            
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

                                            # Enviar com reply_markup usando HTML para evitar conflitos com underline
                                            await bot.send_message(
                                                chat_id=user.telegram_id,
                                                text=formatted_text,
                                                parse_mode="HTML",
                                                reply_markup=markup,
                                                disable_web_page_preview=True
                                            )
                                            custom_message_sent = True
                                            print(f"✅ [Webhooks] Mensagem via arquivo enviada!")
                                        else:
                                            print(f"⚠️ Texto vazio no nó {target_node_id}")
                                    else:
                                        print(f"⚠️ Nó de sucesso não encontrado")
                                else:
                                    print(f"⚠️ Nó de pagamento não encontrado")
                        except Exception as e:
                            print(f"❌ Erro ao processar mensagem via arquivo: {e}")
                    
                    # --- FALLBACK FINAL ---
                    if not custom_message_sent:
                        print("🔄 Usando mensagem padrão como fallback final")
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