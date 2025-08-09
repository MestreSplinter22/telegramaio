from fastapi import FastAPI
from .bot import is_bot_running, get_bot_info

def register_telegram_routes(app: FastAPI):
    """Registra as rotas do Telegram no FastAPI"""
    
    @app.get("/api/telegram/status")
    async def get_bot_status():
        """Retorna o status detalhado do bot do Telegram"""
        info = get_bot_info()
        return {
            "running": info["running"],
            "token_configured": info["token_configured"],
            "token_env_var": info["token_env_var"],
            "application_instance": info["application_instance"],
            "message": "Bot do Telegram está funcionando" if info["running"] else "Bot do Telegram não está rodando",
            "details": info
        }

    @app.post("/api/telegram/start")
    async def start_bot():
        """Inicia o bot do Telegram manualmente"""
        from .bot import start_telegram_bot
        
        try:
            result = await start_telegram_bot()
            if result:
                return {"message": "Bot do Telegram iniciado com sucesso!", "status": "running"}
            else:
                return {"message": "Falha ao iniciar o bot do Telegram", "status": "failed"}
        except Exception as e:
            return {"message": f"Erro ao iniciar bot: {str(e)}", "status": "error"}

    @app.post("/api/telegram/stop")
    async def stop_bot():
        """Para o bot do Telegram"""
        from .bot import stop_telegram_bot
        
        try:
            result = await stop_telegram_bot()
            if result:
                return {"message": "Bot do Telegram parado com sucesso!", "status": "stopped"}
            else:
                return {"message": "Falha ao parar o bot do Telegram", "status": "failed"}
        except Exception as e:
            return {"message": f"Erro ao parar bot: {str(e)}", "status": "error"}
    
    @app.get("/api/telegram/test")
    async def test_bot():
        """Endpoint para testar se o bot está respondendo"""
        info = get_bot_info()
        return {
            "message": "Bot do Telegram integrado com Reflex", 
            "endpoint": "/api/telegram",
            "bot_running": info["running"],
            "token_status": "configured" if info["token_configured"] else "not_configured"
        }