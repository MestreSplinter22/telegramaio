import asyncio
from contextlib import asynccontextmanager
from .bot import start_telegram_bot, stop_telegram_bot

# Variável global para armazenar a aplicação do bot
telegram_app = None

@asynccontextmanager
async def telegram_lifespan(app):
    """
    Lifespan manager para integrar o bot do Telegram com Reflex
    """
    global telegram_app
    
    # Inicialização
    print("Iniciando lifespan do Telegram...")
    try:
        # Iniciar o bot do Telegram
        telegram_app = await start_telegram_bot()
        print("Bot do Telegram iniciado no lifespan")
        
        yield  # Reflex app está rodando
        
    except Exception as e:
        print(f"Erro durante inicialização do Telegram: {e}")
        raise
    
    finally:
        # Cleanup
        print("Encerrando lifespan do Telegram...")
        if telegram_app:
            await stop_telegram_bot(telegram_app)
            telegram_app = None
            print("Bot do Telegram encerrado no lifespan")