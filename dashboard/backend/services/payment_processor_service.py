import logging
import reflex as rx
from datetime import datetime
import json
import os
from ..telegram.bot import bot
from ..models import User, Transaction

# [IMPORTANTE] Importação necessária para criar os botões
from dashboard.backend.telegram.common.keyboard_builder import build_keyboard

logger = logging.getLogger(__name__)

async def start_flow(user_id: str, flow_name: str, data: dict):
    if flow_name == "pix_received":
        await flow_handler(user_id, data)

async def flow_handler(user_id: str, data: dict):
    txid = data.get("txid")
    amount = float(data.get("valor", 0.0))
    
    # [MARCADOR] Se esta mensagem não aparecer no log, o arquivo não foi salvo corretamente
    logger.info(f"🚀 [PixFlow] Iniciando processamento para User {user_id} - TXID {txid}")

    try:
        with rx.session() as session:
            # 1. Buscar Transação
            transaction = session.query(Transaction).filter(
                (Transaction.extra_data == txid) | (Transaction.id == txid)
            ).first()

            if not transaction:
                logger.error(f"❌ [PixFlow] Transação não encontrada: {txid}")
                return

            if transaction.status == "completed":
                logger.info(f"⚠️ [PixFlow] Transação {txid} já estava concluída.")
                return

            transaction.status = "completed"
            transaction.updated_at = datetime.utcnow()
            
            # 2. Atualizar Saldo do Usuário
            user = session.query(User).filter(User.telegram_id == str(user_id)).first()
            if user:
                user.balance += amount
                user.total_spent += amount
                session.add(user)
                
                # --- Lógica da Mensagem Personalizada ---
                custom_message_sent = False
                
                try:
                    # Carregar fluxo
                    flow_file_path = "dashboard/backend/telegram/flows/start_flow.json"
                    screens = {}
                    if os.path.exists(flow_file_path):
                        with open(flow_file_path, "r", encoding="utf-8") as f:
                            flow_data = json.load(f)
                        screens = flow_data.get("screens", {})

                    # Recuperar screen_id da transação (para saber qual botão gerou o pagto)
                    extra_data = json.loads(transaction.extra_data) if transaction.extra_data else {}
                    payment_screen_id = extra_data.get("screen_id")
                    
                    logger.info(f"🔍 [PixFlow] Screen ID de origem: {payment_screen_id}")

                    if payment_screen_id and payment_screen_id in screens:
                        payment_node = screens[payment_screen_id]
                        target_node_id = payment_node.get("webhook")
                        
                        if target_node_id and target_node_id in screens:
                            success_node = screens[target_node_id]
                            message_text = success_node.get("text", "")
                            
                            if message_text:
                                formatted_text = message_text.replace("{amount}", f"{amount:.2f}")\
                                                             .replace("{txid}", txid)
                                
                                # --- [CORREÇÃO] Construir Botões ---
                                markup = None
                                buttons_data = success_node.get("buttons")
                                
                                if buttons_data:
                                    logger.info(f"🔘 [PixFlow] Botões encontrados: {buttons_data}")
                                    try:
                                        markup = build_keyboard(buttons_data)
                                    except Exception as kb_err:
                                        logger.error(f"❌ [PixFlow] Erro no teclado: {kb_err}")
                                # -----------------------------------

                                # Enviar mensagem COM o teclado (reply_markup)
                                await bot.send_message(
                                    chat_id=int(user.telegram_id),
                                    text=formatted_text,
                                    parse_mode="Markdown",
                                    reply_markup=markup  # <--- O botão é enviado aqui
                                )
                                custom_message_sent = True
                                logger.info(f"✅ [PixFlow] Mensagem enviada para {target_node_id}")
                            else:
                                logger.warning(f"⚠️ [PixFlow] Nó {target_node_id} sem texto.")
                        else:
                            logger.warning(f"⚠️ [PixFlow] Nó de webhook {target_node_id} não existe.")
                    else:
                        logger.warning(f"⚠️ [PixFlow] Nó de pagamento {payment_screen_id} não existe.")

                except Exception as e:
                    logger.error(f"❌ [PixFlow] Erro na lógica customizada: {e}", exc_info=True)
                
                # Fallback (Mensagem Padrão)
                if not custom_message_sent:
                    logger.info("🔄 [PixFlow] Enviando mensagem padrão.")
                    await bot.send_message(
                        chat_id=int(user.telegram_id),
                        text=(
                            f"✅ <b>Pagamento Confirmado!</b>\n\n"
                            f"💵 Valor: R$ {amount:.2f}\n"
                            f"🆔 TXID: <code>{txid}</code>\n\n"
                            f"Seu saldo foi atualizado."
                        ),
                        parse_mode="HTML"
                    )

            session.add(transaction)
            session.commit()
            logger.info(f"🏁 [PixFlow] Finalizado com sucesso.")

    except Exception as e:
        logger.error(f"❌ [PixFlow] Erro Crítico: {e}", exc_info=True)