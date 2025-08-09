import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from .startup import startup_telegram_bot, shutdown_telegram_bot

# Carregar variáveis de ambiente do arquivo .env
dotenv_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / '.env'
load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

# Inicialização automática do bot
def init_telegram_bot():
    """Inicializa o bot do Telegram de forma síncrona"""
    try:
        # Criar event loop se não existir
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Executar inicialização
        if loop.is_running():
            logger.info("Bot do Telegram será iniciado pelo lifespan")
        else:
            logger.info("Inicializando bot do Telegram...")
            # Não iniciar aqui, deixar para o lifespan
    except Exception as e:
        logger.error(f"Erro na inicialização do bot: {e}")

# Executar inicialização
init_telegram_bot()

__all__ = ['startup_telegram_bot', 'shutdown_telegram_bot']