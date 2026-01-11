# dashboard/backend/telegram/handlers/debug_callback_handler.py

from aiogram import Router, types
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query()
async def debug_all_callbacks(callback: types.CallbackQuery):
    """
    Handler de debug que captura TODOS os callbacks não tratados.
    Use isso para descobrir qual callback_data está sendo enviado.
    """
    logger.info(f"🔍 CALLBACK RECEBIDO: data='{callback.data}' | user={callback.from_user.id} | username=@{callback.from_user.username}")
    logger.info(f"📋 Callback completo: {callback}")
    
    await callback.answer(f"Debug: Callback '{callback.data}' recebido!", show_alert=True)