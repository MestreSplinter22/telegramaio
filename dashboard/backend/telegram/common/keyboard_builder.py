from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import logging

logger = logging.getLogger(__name__)

def create_button(btn_data: dict) -> InlineKeyboardButton:
    """
    Cria um botão baseado no dicionário de configuração.
    Suporta: callback_data, url, web_app.
    """
    text = btn_data.get("text", "Botão")
    
    # LOG DE DEBUG
    logger.debug(f"🔧 Criando botão: text='{text}', dados={btn_data}")
    
    # PRIORIDADE 1: callback_data (para handlers)
    if "callback_data" in btn_data and btn_data["callback_data"]:
        logger.debug(f"✅ Botão '{text}' com callback_data='{btn_data['callback_data']}'")
        return InlineKeyboardButton(text=text, callback_data=btn_data["callback_data"])
    
    # PRIORIDADE 2: callback (alias antigo)
    if "callback" in btn_data and btn_data["callback"]:
        logger.debug(f"✅ Botão '{text}' com callback='{btn_data['callback']}'")
        return InlineKeyboardButton(text=text, callback_data=btn_data["callback"])
    
    # PRIORIDADE 3: url
    if "url" in btn_data and btn_data["url"]:
        logger.debug(f"✅ Botão '{text}' com url='{btn_data['url']}'")
        return InlineKeyboardButton(text=text, url=btn_data["url"])
        
    # PRIORIDADE 4: web_app
    if "web_app" in btn_data and btn_data["web_app"]:
        logger.debug(f"✅ Botão '{text}' com web_app='{btn_data['web_app']}'")
        return InlineKeyboardButton(text=text, web_app=WebAppInfo(url=btn_data["web_app"]))

    # FALLBACK: Se nada foi encontrado
    logger.warning(f"⚠️ Botão '{text}' sem callback/url definido. Dados: {btn_data}")
    return InlineKeyboardButton(text=text, callback_data="undefined_action")

def build_keyboard(rows: list) -> InlineKeyboardMarkup:
    """
    Recebe uma lista de listas (linhas de botões) do JSON e retorna o Markup.
    """
    logger.debug(f"🔨 Construindo teclado com {len(rows)} linha(s)")
    keyboard = []
    for i, row in enumerate(rows):
        logger.debug(f"  Linha {i}: {len(row)} botão(ões)")
        keyboard_row = [create_button(btn) for btn in row]
        keyboard.append(keyboard_row)
    
    logger.debug(f"✅ Teclado construído com sucesso")
    return InlineKeyboardMarkup(inline_keyboard=keyboard)