import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Token do bot - usar variável de ambiente ou fallback
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logger.debug(f"Variáveis de ambiente carregadas: TELEGRAM_BOT_TOKEN={'definido' if BOT_TOKEN else 'não definido'}")
logger.debug(f"Valor do token: {BOT_TOKEN[:10]}... (primeiros caracteres)" if BOT_TOKEN else "Token não definido")

# Usar o token hardcoded se não estiver definido na variável de ambiente
if not BOT_TOKEN:
    BOT_TOKEN = "7117120727:AAH_CUBJP5qa-x8sxQ3KAWYsmIJp3-tD3E0"
    logger.debug("Usando token hardcoded como fallback")

# Variável global para verificar se o bot está rodando
bot_running = False
application_instance = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /start"""
    await update.message.reply_text("Hello World! Bot iniciado com sucesso!")

async def start_telegram_bot():
    """Inicia o bot do Telegram"""
    global bot_running, application_instance
    
    if not BOT_TOKEN:
        logger.error("❌ Token do bot não configurado! Defina TELEGRAM_BOT_TOKEN no ambiente.")
        return None
        
    logger.info(f"Iniciando bot com token: {BOT_TOKEN[:10]}...")
    logger.debug(f"Token completo: {BOT_TOKEN}")
    
    try:
        logger.info("Criando aplicação do bot...")
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Adicionar handlers
        logger.info("Adicionando handlers...")
        application.add_handler(CommandHandler("start", start_command))
        
        # Iniciar o bot
        logger.info("Inicializando aplicação...")
        await application.initialize()
        await application.start()
        
        logger.info("Iniciando polling...")
        await application.updater.start_polling(timeout=30)
        
        bot_running = True
        application_instance = application
        logger.info("✅ Bot do Telegram iniciado com sucesso!")
        logger.info("Bot está aguardando comandos...")
        
        return application
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar o bot: {e}")
        bot_running = False
        return None

async def stop_telegram_bot(application=None):
    """Para o bot do Telegram"""
    global bot_running, application_instance
    app_to_stop = application or application_instance
    
    try:
        if app_to_stop:
            await app_to_stop.stop()
            await app_to_stop.shutdown()
            bot_running = False
            application_instance = None
            logger.info("Bot do Telegram encerrado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao parar o bot: {e}")

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