# dashboard/backend/api/gateways/webhooks.py

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
        Processa webhook da SuitPay (Mantido inalterado)
        """
        try:
            data = await request.json()
            print(f"🔔 Webhook SuitPay Recebido: {data}")
        except:
            return {"status": "error", "msg": ERROR_INVALID_JSON}

        if data.get("statusTransaction") != WEBHOOK_STATUS_PAID_OUT:
            return {"status": "ignored", "reason": "Not PAID_OUT"}

        request_number = data.get("requestNumber")
        
        with rx.session() as session:
            txns = session.query(Transaction).filter(Transaction.status == "pending").all()
            txn = None
            for t in txns:
                if t.extra_data and (str(request_number) in t.extra_data):
                    txn = t
                    break
            
            if txn:
                valor_pago = float(data.get("value", 0))
                if abs(txn.amount - valor_pago) > VALUE_TOLERANCE:
                    return {"status": "error", "msg": ERROR_VALUE_MISMATCH}

                txn.status = "completed"
                session.add(txn)
                
                user = session.query(User).filter(User.telegram_id == txn.user_id).first()
                if user:
                    user.balance += txn.amount
                    user.total_spent += txn.amount
                    session.add(user)
                    try:
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=f"✅ <b>Pagamento Confirmado!</b>\n\n💰 Crédito de R$ {txn.amount:.2f} adicionado à sua conta.",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        print(f"Erro ao notificar Telegram: {e}")
                
                session.commit()
                return {"response": "OK"}
                
        return {"status": "not_found"}

    @staticmethod
    async def process_openpix_webhook(request: Request) -> Dict[str, Any]:
        """
        Processa webhook da OpenPix com suporte a mensagens customizadas do remarketing
        """
        # DEFINIÇÃO DO CAMINHO DO ARQUIVO AQUI DENTRO PARA EVITAR ERROS
        REMARKETING_FLOW_PATH = "dashboard/backend/telegram/flows/remarketing.json"
        
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
                    
                    # --- TENTATIVA 1: DADOS DE REMARKETING (Metadados Diretos) ---
                    try:
                        extra_data = json.loads(txn.extra_data) if txn.extra_data else {}
                        success_screen_id = extra_data.get("success_screen_id")
                        remarketing_data = extra_data.get("remarketing_success_data")
                        
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
                        print(f"❌ Erro remarketing prioridade 1: {e_remarketing}")
                    
                    # --- TENTATIVA 2: ARQUIVO DE FLUXO (Mesclando start_flow.json e remarketing.json) ---
                    if not custom_message_sent:
                        try:
                            print(f"🔍 [Webhooks] Buscando fluxo nos arquivos JSON para TXID: {txid}")
                            
                            screens = {}
                            
                            # 1. Carregar fluxo principal (start_flow.json)
                            if os.path.exists(FLOW_FILE_PATH):
                                with open(FLOW_FILE_PATH, "r", encoding="utf-8") as f:
                                    main_flow = json.load(f)
                                    screens.update(main_flow.get("screens", {}))
                            
                            # 2. Carregar e MESCLAR fluxo de remarketing (remarketing.json)
                            if os.path.exists(REMARKETING_FLOW_PATH):
                                try:
                                    with open(REMARKETING_FLOW_PATH, "r", encoding="utf-8") as rf:
                                        rem_flow = json.load(rf)
                                        # Mescla apenas a chave "screens" se existir, ou o próprio dict se for direto
                                        rem_screens = rem_flow.get("screens", rem_flow) 
                                        screens.update(rem_screens)
                                    print("📂 [Webhooks] Arquivo remarketing.json carregado e mesclado.")
                                except Exception as e:
                                    print(f"⚠️ Falha ao ler remarketing.json: {e}")
                            else:
                                print(f"⚠️ Arquivo remarketing.json não encontrado em: {REMARKETING_FLOW_PATH}")

                            # 3. Identificar tela de pagamento
                            payment_screen_id = None
                            try:
                                extra_data = json.loads(txn.extra_data) if txn.extra_data else {}
                                payment_screen_id = extra_data.get("screen_id")
                            except: pass
                            
                            # 4. Processar Webhook
                            if payment_screen_id and payment_screen_id in screens:
                                payment_node = screens[payment_screen_id]
                                target_node_id = payment_node.get("webhook")
                                print(f"🔗 Webhook aponta para nó: {target_node_id}")
                                
                                if target_node_id and target_node_id in screens:
                                    success_node = screens[target_node_id]
                                    message_text = success_node.get("text", "")
                                    
                                    if message_text:
                                        # Formatações
                                        formatted_text = message_text.replace("{amount}", f"{txn.amount:.2f}")\
                                                                     .replace("{txid}", txid)\
                                                                     .replace("{first_name}", user.first_name)
                                        
                                        markup = None
                                        if "buttons" in success_node and success_node["buttons"]:
                                            markup = build_keyboard(success_node["buttons"])

                                        await bot.send_message(
                                            chat_id=user.telegram_id,
                                            text=formatted_text,
                                            parse_mode="HTML",
                                            reply_markup=markup,
                                            disable_web_page_preview=True
                                        )
                                        custom_message_sent = True
                                        print(f"✅ [Webhooks] Mensagem enviada via JSON com sucesso!")
                                    else:
                                        print(f"⚠️ Texto vazio no nó {target_node_id}")
                                else:
                                    print(f"⚠️ Nó de sucesso '{target_node_id}' não encontrado nos JSONs carregados.")
                            else:
                                print(f"⚠️ Nó de pagamento '{payment_screen_id}' não encontrado.")

                        except Exception as e:
                            print(f"❌ Erro ao processar mensagem via arquivo: {e}")
                    
                    # --- FALLBACK FINAL ---
                    if not custom_message_sent:
                        print("🔄 Usando mensagem padrão como fallback final")
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=f"✅ <b>Pagamento Confirmado!</b>\n\n💰 + R$ {txn.amount:.2f}",
                            parse_mode="HTML"
                        )
                
                session.commit()
                return {"status": "ok"}
        
        return {"status": "not_found"}

class EfiWebhookService:
    @staticmethod
    async def process_efi_webhook(request: Request) -> Dict[str, Any]:
        return {"status": "ok"}