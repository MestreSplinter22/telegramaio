import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties 

# --- IMPORTAÇÕES DE HANDLERS ---
from dashboard.backend.telegram.handlers.start_handler import router as start_router
from dashboard.backend.telegram.handlers.flow_handler import router as flow_router
from dashboard.backend.telegram.handlers.join_handler import router as join_router
from dashboard.backend.telegram.handlers.remarketing_handler import router as remarketing_router
from dashboard.backend.telegram.handlers.debug_callback_handler import router as debug_router  # DEBUG

# --- IMPORTAÇÃO DO MIDDLEWARE ---
try:
    from .logger import InteractionLoggerMiddleware
except ImportError:
    from dashboard.backend.telegram.utils.logger import InteractionLoggerMiddleware

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Token do bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logger.debug(f"Variáveis de ambiente carregadas: TELEGRAM_BOT_TOKEN={'definido' if BOT_TOKEN else 'não definido'}")
logger.debug(f"Valor do token: {BOT_TOKEN[:10]}... (primeiros caracteres)" if BOT_TOKEN else "Token não definido")

if not BOT_TOKEN:
    BOT_TOKEN = "7117120727:AAH_CUBJP5qa-x8sxQ3KAWYsmIJp3-tD3E0"
    logger.debug("Usando token hardcoded como fallback")

# Variáveis de controle
bot_running = False
application_instance = None
dispatcher_instance = None

# Instância do bot
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# --- REGISTRO DO MIDDLEWARE ---
dp.update.outer_middleware(InteractionLoggerMiddleware())

@dp.message(Command("help"))
async def help_command(message: Message) -> None:
    """Handler para o comando /help"""
    await message.answer("Comandos disponíveis:\n/start - Iniciar o bot\n/help - Ajuda")

async def start_telegram_bot():
    """Inicia o bot do Telegram usando aiogram"""
    global bot_running, application_instance, dispatcher_instance
    
    if not BOT_TOKEN:
        logger.error("❌ Token do bot não configurado! Defina TELEGRAM_BOT_TOKEN no ambiente.")
        return None
        
    logger.info(f"Iniciando bot com token: {BOT_TOKEN[:10]}...")
    
    try:
        logger.info("Inicializando bot com aiogram...")
        
        # Registrar handlers no dispatcher
        logger.info("Registrando handlers...")
        if start_router not in dp.sub_routers:
            dp.include_router(start_router)
        if flow_router not in dp.sub_routers:
            dp.include_router(flow_router)
        if join_router not in dp.sub_routers:
            dp.include_router(join_router)
            logger.info("Router de Join Request registrado.")
        # NOVO: Registrar handler de remarketing ANTES do debug
        if remarketing_router not in dp.sub_routers:
            dp.include_router(remarketing_router)
            logger.info("✅ Router de Remarketing registrado.")
        # DEBUG: Registrar por último para capturar callbacks não tratados
        if debug_router not in dp.sub_routers:
            dp.include_router(debug_router)
            logger.info("🔍 Router de Debug registrado (captura callbacks não tratados).")
        
        # Iniciar o polling
        logger.info("Iniciando polling...")
        
        # Criar task para o dispatcher
        task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
        
        bot_running = True
        application_instance = task
        dispatcher_instance = dp
        logger.info("✅ Bot do Telegram iniciado com sucesso (Middleware Ativo + Remarketing Handler)!")
        
        return task
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar o bot: {e}")
        bot_running = False
        return None

async def stop_telegram_bot(application=None):
    """Para o bot do Telegram"""
    global bot_running, application_instance, dispatcher_instance
    
    try:
        if application_instance:
            logger.info("Parando bot do Telegram...")
            if dispatcher_instance:
                await dispatcher_instance.stop_polling()
            
            bot_running = False
            application_instance = None
            dispatcher_instance = None
            logger.info("Bot do Telegram encerrado com sucesso!")
            return True
        return True
    except Exception as e:
        logger.error(f"Erro ao parar o bot: {e}")
        return False

def is_bot_running():
    """Retorna True se o bot está rodando"""
    return bot_running and application_instance is not None

def get_bot_info():
    """Retorna informações detalhadas sobre o bot"""
    return {
        "running": bot_running,
        "token_configured": BOT_TOKEN is not None,
        "token_env_var": os.getenv("TELEGRAM_BOT_TOKEN") is not None,
        "token_length": len(BOT_TOKEN) if BOT_TOKEN else 0,
        "application_instance": application_instance is not None
    }