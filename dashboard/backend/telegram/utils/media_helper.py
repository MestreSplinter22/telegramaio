# dashboard/backend/telegram/utils/media_helper.py

import base64
from typing import Union

from aiogram import types
from aiogram.types import BufferedInputFile


class MediaHelper:
    @staticmethod
    def base64_to_buffered_input_file(base64_string: str, filename: str = "image.png") -> BufferedInputFile:
        """Converte uma string base64 em um BufferedInputFile para envio pelo Telegram."""
        # Remove o prefixo data:image se existir
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        # Limpa a string base64
        base64_string = base64_string.strip().replace("\n", "").replace("\r", "")
        
        # Decodifica a string base64 para bytes
        try:
            img_bytes = base64.b64decode(base64_string)
            return BufferedInputFile(img_bytes, filename=filename)
        except Exception as e:
            raise ValueError(f"Erro ao decodificar base64: {str(e)}")

    @staticmethod
    def clean_image_source(image_source: str) -> str:
        """Limpa e padroniza uma string de imagem."""
        if not image_source:
            return image_source
            
        # Remove prefixos de data URI se existirem
        if image_source.startswith("data:image"):
            image_source = image_source.split(",")[1]
        
        # Limpa espaços e quebras de linha
        return image_source.strip().replace("\n", "").replace("\r", "")

    @staticmethod
    def detect_parse_mode(text: str) -> str:
        """Detecta automaticamente o modo de parse (HTML ou Markdown) com base no conteúdo."""
        if "*" in text or "_" in text or "[" in text or "]" in text:
            return "Markdown"
        return "HTML"

    @staticmethod
    def is_valid_base64_image(image_source: str) -> bool:
        """Verifica se a string é uma imagem base64 válida."""
        try:
            if "," in image_source:
                image_source = image_source.split(",")[1]
            
            image_source = image_source.strip().replace("\n", "").replace("\r", "")
            base64.b64decode(image_source)
            return True
        except Exception:
            return False