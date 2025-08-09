import asyncio
import logging
from typing import Optional
from telegram.ext import Application
from .bot import start_telegram_bot, stop_telegram_bot

logger = logging.getLogger(__name__)
telegram_app: Optional[Application] = None

async def startup_telegram_bot():
    """Inicia o bot do Telegram quando o Reflex iniciar"""
    global telegram_app
    
    try:
        logger.info("Iniciando bot do Telegram...")
        telegram_app = await start_telegram_bot()
        logger.info("Bot do Telegram iniciado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao iniciar bot do Telegram: {e}")
        return False

async def shutdown_telegram_bot():
    """Para o bot do Telegram quando o Reflex encerrar"""
    global telegram_app
    
    try:
        if telegram_app:
            logger.info("Encerrando bot do Telegram...")
            await stop_telegram_bot(telegram_app)
            telegram_app = None
            logger.info("Bot do Telegram encerrado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao encerrar bot do Telegram: {e}")