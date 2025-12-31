import logging
import reflex as rx
from datetime import datetime
import json
import os
from ..telegram.bot import bot
from ..models import User, Transaction

logger = logging.getLogger(__name__)

async def start_flow(user_id: str, flow_name: str, data: dict):
    """
    Inicia um fluxo específico. Compatível com a assinatura solicitada.
    """
    if flow_name == "pix_received":
        await flow_handler(user_id, data)

async def flow_handler(user_id: str, data: dict):
    """
    Manipula a lógica de recebimento do Pix:
    1. Atualiza status da transação
    2. Adiciona saldo ao usuário
    3. Envia mensagem no Telegram
    """
    txid = data.get("txid")
    amount = float(data.get("valor", 0.0))
    end_to_end_id = data.get("endToEndId")

    logger.info(f"Iniciando flow de Pix para User {user_id} - TXID {txid}")

    try:
        with rx.session() as session:
            # 1. Buscar e Atualizar a Transação
            # Assumindo que o ID da transação ou extra_data guarda o txid
            transaction = session.query(Transaction).filter(
                (Transaction.extra_data == txid) | (Transaction.id == txid)
            ).first()

            if not transaction:
                logger.error(f"Transação não encontrada para TXID: {txid}")
                return

            if transaction.status == "completed":
                logger.info("Transação já processada anteriormente.")
                return

            transaction.status = "completed"
            transaction.updated_at = datetime.utcnow()
            
            # 2. Atualizar Saldo do Usuário
            user = session.query(User).filter(User.telegram_id == str(user_id)).first()
            if user:
                user.balance += amount
                user.total_spent += amount # Ajuste conforme sua lógica de 'spent' vs 'deposit'
                session.add(user)
                
                # --- NOVA LÓGICA DE MENSAGEM PERSONALIZADA ---
                custom_message_sent = False
                
                try:
                    logger.info(f"🔍 Iniciando processamento de mensagem personalizada para TXID: {txid}")
                    
                    # 1. Carregar o fluxo para consultar os nós
                    flow_file_path = "dashboard/backend/telegram/flows/start_flow.json"
                    if os.path.exists(flow_file_path):
                        with open(flow_file_path, "r", encoding="utf-8") as f:
                            flow_data = json.load(f)
                        screens = flow_data.get("screens", {})
                        logger.info(f"📄 Fluxo carregado com {len(screens)} telas")
                        
                        # 2. Identificar qual era a tela de pagamento associada a essa transação
                        # Procurar nos metadados da transação pelo screen_id
                        payment_screen_id = None
                        logger.info(f"📦 Extra data da transação: {transaction.extra_data}")
                        
                        try:
                            extra_data = json.loads(transaction.extra_data) if transaction.extra_data else {}
                            payment_screen_id = extra_data.get("screen_id")
                            logger.info(f"🎯 Screen ID encontrado nos metadados: {payment_screen_id}")
                        except Exception as e:
                            logger.error(f"❌ Erro ao parsear extra_data: {e}")
                            # Se não conseguir parsear, tenta usar o txid como fallback
                            pass
                        
                        # 3. Se encontrou o nó de pagamento, verificar se tem webhook
                        if payment_screen_id and payment_screen_id in screens:
                            logger.info(f"✅ Nó de pagamento {payment_screen_id} encontrado no fluxo")
                            payment_node = screens[payment_screen_id]
                            target_node_id = payment_node.get("webhook")
                            logger.info(f"🔗 Webhook aponta para: {target_node_id}")
                            
                            # 4. Se tem nó de sucesso, buscar a mensagem personalizada
                            if target_node_id and target_node_id in screens:
                                logger.info(f"✅ Nó de sucesso {target_node_id} encontrado")
                                success_node = screens[target_node_id]
                                message_text = success_node.get("text", "")
                                logger.info(f"💬 Texto da mensagem: {message_text}")
                                
                                if message_text:
                                    # Formatar a mensagem (substituir variáveis)
                                    formatted_text = message_text.replace("{amount}", f"{amount:.2f}")
                                    formatted_text = formatted_text.replace("{txid}", txid)
                                    logger.info(f"✉️ Mensagem formatada: {formatted_text}")
                                    
                                    # 5. Enviar a mensagem personalizada
                                    await bot.send_message(
                                        chat_id=int(user.telegram_id),
                                        text=formatted_text,
                                        parse_mode="Markdown"
                                    )
                                    custom_message_sent = True
                                    logger.info(f"✅ Mensagem personalizada enviada para o nó {target_node_id}")
                                else:
                                    logger.warning(f"⚠️ Texto vazio no nó {target_node_id}")
                            else:
                                logger.warning(f"⚠️ Nó de sucesso {target_node_id} não encontrado no fluxo")
                        else:
                            logger.warning(f"⚠️ Nó de pagamento {payment_screen_id} não encontrado no fluxo")
                            logger.info(f"🔍 Telas disponíveis: {list(screens.keys())}")
                except Exception as e:
                    logger.error(f"❌ Erro ao processar mensagem personalizada: {e}", exc_info=True)
                
                # 6. Fallback: Se não encontrou mensagem customizada, envia a padrão
                if not custom_message_sent:
                    logger.warning("🔄 Usando mensagem padrão como fallback")
                    try:
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
                        logger.info("✅ Mensagem padrão enviada com sucesso")
                    except Exception as e:
                        logger.error(f"❌ Erro ao enviar mensagem Telegram (padrão): {e}")

            session.add(transaction)
            session.commit()
            logger.info(f"Flow finalizado com sucesso para TXID {txid}")

    except Exception as e:
        logger.error(f"Erro crítico no flow_handler: {e}")