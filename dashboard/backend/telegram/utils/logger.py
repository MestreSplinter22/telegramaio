import json
import os
import aiofiles # Recomendado para I/O assíncrono, mas pode usar open() padrão se o tráfego for baixo
from datetime import datetime
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

# Nome do arquivo onde os logs serão salvos
LOG_FILE = "user_interactions.json"

async def save_to_json(user_id: int, interaction_data: dict):
    """
    Função que lê o arquivo JSON existente, adiciona o novo log e salva novamente.
    """
    new_entry = {
        "user_id": user_id,
        "log": interaction_data,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    logs = []
    
    # Verifica se o arquivo já existe e lê o conteúdo
    if os.path.exists(LOG_FILE):
        try:
            async with aiofiles.open(LOG_FILE, mode='r', encoding='utf-8') as f:
                content = await f.read()
                if content:
                    logs = json.loads(content)
        except json.JSONDecodeError:
            logs = [] # Se o arquivo estiver corrompido, inicia uma lista vazia

    logs.append(new_entry)

    # Escreve o conteúdo atualizado no arquivo
    async with aiofiles.open(LOG_FILE, mode='w', encoding='utf-8') as f:
        await f.write(json.dumps(logs, indent=4, ensure_ascii=False))

class InteractionLoggerMiddleware(BaseMiddleware):
    """
    Middleware do Aiogram para interceptar todas as atualizações.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Tenta obter o usuário que originou o evento
        user = data.get("event_from_user")
        
        if user:
            # Prepara os dados agnósticos (converte o objeto do telegram para dict)
            # O método .model_dump() (pydantic v2) ou .dict() é usado no aiogram 3
            if hasattr(event, 'model_dump'):
                event_data = event.model_dump(exclude_none=True)
            elif hasattr(event, 'dict'):
                event_data = event.dict(exclude_none=True)
            else:
                event_data = str(event)

            # Salva o log de forma assíncrona para não travar o bot
            await save_to_json(user.id, event_data)

        # Passa o controle para o próximo handler
        return await handler(event, data)