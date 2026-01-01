# dashboard/backend/telegram/handlers/join_handler.py

import logging
import reflex as rx
from aiogram import Router, types
from sqlmodel import select
from dashboard.backend.models.transaction import Transaction

# Configura o logger para debug
logger = logging.getLogger(__name__)

router = Router()

@router.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest):
    """
    Handler automático para aceitar ou recusar pedidos de entrada.
    Verifica se o usuário possui uma transação 'completed' no banco.
    """
    user_id = str(update.from_user.id)
    user_name = update.from_user.first_name
    chat_id = update.chat.id
    
    logger.info(f"Recebido pedido de entrada de {user_name} ({user_id}) no canal {chat_id}")

    try:
        # Abre uma sessão com o banco de dados usando o Reflex
        with rx.session() as session:
            # Query: Busca transação do usuário com status 'completed'
            statement = select(Transaction).where(
                Transaction.user_id == user_id,
                Transaction.status == "completed"
            )
            # Tenta pegar o primeiro resultado
            transaction = session.exec(statement).first()

            if transaction:
                # Se encontrou transação paga, ACEITA
                await update.approve()
                logger.info(f"✅ Pedido de {user_name} APROVADO (Transação ID: {transaction.id})")
                
                # Opcional: Mandar mensagem privada avisando
                # await update.bot.send_message(user_id, "✅ Seu acesso foi aprovado! Bem-vindo.")
            else:
                # Se não encontrou ou não está pago, RECUSA
                await update.decline()
                logger.info(f"❌ Pedido de {user_name} RECUSADO (Sem transação concluída)")

    except Exception as e:
        logger.error(f"Erro ao processar pedido de entrada: {e}")
        # Por segurança, você pode optar por não fazer nada ou recusar em caso de erro