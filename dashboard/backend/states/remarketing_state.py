# dashboard/backend/states/remarketing_state.py

import reflex as rx
from sqlmodel import select
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
from pydantic import BaseModel  # <--- NOVA IMPORTAÇÃO

from dashboard.backend.database import get_db_session
from dashboard.backend.models.transaction import Transaction
from dashboard.backend.models.user import User
from dashboard.backend.telegram.bot import bot
from dashboard.backend.telegram.common.keyboard_builder import build_keyboard

# --- MODELOS DE DADOS PARA O EDITOR (Atualizado para BaseModel) ---
class RemarketingButton(BaseModel):  # <--- Mudou de rx.Base para BaseModel
    text: str = "Botão"
    type: str = "url"  # 'url' ou 'callback'
    url: str = ""
    callback: str = ""

class RemarketingBlock(BaseModel):   # <--- Mudou de rx.Base para BaseModel
    text: str = ""
    image_url: str = ""
    video_url: str = ""
    # Estrutura: Lista de Linhas, onde cada Linha é uma Lista de Botões
    buttons: List[List[RemarketingButton]] = []

class RemarketingState(rx.State):
    # --- DADOS DA AUDIÊNCIA ---
    pending_users: List[Dict[str, Any]] = []
    loading_users: bool = False
    
    # --- DADOS DO EDITOR ---
    editor_blocks: List[RemarketingBlock] = [
        RemarketingBlock(
            text="Olá {first_name}! 🔔\n\nNotamos que você gerou um pedido de R$ {amount} mas ainda não finalizou.\n\nClique abaixo para pagar agora!",
            buttons=[
                [RemarketingButton(text="💳 Pagar Agora", type="url", url="https://t.me/seubot?start=pagar")]
            ]
        )
    ]
    
    temp_badge_url: str = ""

    def load_pending_users(self):
        """Busca usuários com transações pendentes há mais de 15 minutos."""
        self.loading_users = True
        yield
        
        try:
            with get_db_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(minutes=15)
                
                statement = select(Transaction, User).where(
                    Transaction.user_id == User.telegram_id,
                    Transaction.status == "pending",
                    Transaction.timestamp < cutoff_time
                )
                results = session.exec(statement).all()
                
                users_data = []
                seen_ids = set()
                
                for txn, user in results:
                    if user.telegram_id not in seen_ids:
                        time_diff = datetime.utcnow() - txn.timestamp
                        minutes_pending = int(time_diff.total_seconds() / 60)
                        
                        users_data.append({
                            "telegram_id": user.telegram_id,
                            "first_name": user.first_name,
                            "username": user.username or "Sem user",
                            "amount": f"{txn.amount:.2f}",
                            "minutes_pending": minutes_pending,
                            "txn_id": txn.id
                        })
                        seen_ids.add(user.telegram_id)
                
                self.pending_users = users_data
        except Exception as e:
            print(f"Erro ao carregar usuários: {e}")
        finally:
            self.loading_users = False
            yield

    async def send_remarketing_campaign(self):
        """Envia a mensagem configurada para todos os usuários da lista."""
        if not self.pending_users:
            return rx.window_alert("Nenhum usuário encontrado para remarketing.")
        
        if not self.editor_blocks:
            return rx.window_alert("Configure a mensagem antes de enviar.")

        # Converte o objeto Block para dict para usar na função de envio existente
        block_obj = self.editor_blocks[0]
        block_dict = block_obj.dict()
        
        success_count = 0
        fail_count = 0
        
        for user in self.pending_users:
            chat_id = user["telegram_id"]
            context = {
                "first_name": user["first_name"],
                "username": user["username"],
                "amount": user["amount"]
            }
            
            try:
                await self._send_proactive_message(chat_id, block_dict, context)
                success_count += 1
                await asyncio.sleep(0.1) 
            except Exception as e:
                print(f"Falha ao enviar para {chat_id}: {e}")
                fail_count += 1
        
        return rx.window_alert(f"Disparo concluído!\n✅ Enviados: {success_count}\n❌ Falhas: {fail_count}")

    async def _send_proactive_message(self, chat_id: str, template: dict, context: dict):
        text = template.get("text", "")
        try:
            text = text.format(**context)
        except KeyError:
            pass 
            
        markup = None
        if "buttons" in template and template["buttons"]:
            markup = build_keyboard(template["buttons"])
            
        parse_mode = "HTML"
        image_url = template.get("image_url")
        video_url = template.get("video_url")
        
        if video_url:
            await bot.send_video(chat_id=chat_id, video=video_url, caption=text, reply_markup=markup, parse_mode=parse_mode)
        elif image_url:
            await bot.send_photo(chat_id=chat_id, photo=image_url, caption=text, reply_markup=markup, parse_mode=parse_mode)
        else:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode=parse_mode)

    # --- MÉTODOS DE EDIÇÃO ---
    
    def update_block_text(self, index: int, text: str):
        if 0 <= index < len(self.editor_blocks):
            self.editor_blocks[index].text = text

    def set_media_type(self, index: int, type: str):
        if 0 <= index < len(self.editor_blocks):
            self.editor_blocks[index].image_url = ""
            self.editor_blocks[index].video_url = ""
            
            if type == "image": 
                self.editor_blocks[index].image_url = "https://..."
            elif type == "video": 
                self.editor_blocks[index].video_url = "https://..."

    def update_media_url(self, index: int, key: str, value: str):
        if 0 <= index < len(self.editor_blocks):
            if key == "image_url":
                self.editor_blocks[index].image_url = value
            elif key == "video_url":
                self.editor_blocks[index].video_url = value

    def add_button_row(self, block_index: int):
        if 0 <= block_index < len(self.editor_blocks):
            new_btn = RemarketingButton(text="Botão", url="https://...")
            self.editor_blocks[block_index].buttons.append([new_btn])

    def add_button_to_row(self, block_index: int, row_index: int):
        if 0 <= block_index < len(self.editor_blocks):
            buttons_list = self.editor_blocks[block_index].buttons
            if 0 <= row_index < len(buttons_list):
                new_btn = RemarketingButton(text="Botão", url="https://...")
                buttons_list[row_index].append(new_btn)
                self.editor_blocks[block_index].buttons = buttons_list

    def remove_button(self, block_index: int, row_index: int, btn_index: int):
        if 0 <= block_index < len(self.editor_blocks):
            buttons_list = self.editor_blocks[block_index].buttons
            if 0 <= row_index < len(buttons_list):
                row = buttons_list[row_index]
                if 0 <= btn_index < len(row):
                    row.pop(btn_index)
                    if not row:
                        buttons_list.pop(row_index)
                    self.editor_blocks[block_index].buttons = buttons_list

    def update_button(self, block_idx: int, row_idx: int, btn_idx: int, field: str, value: str):
        if 0 <= block_idx < len(self.editor_blocks):
            buttons_list = self.editor_blocks[block_idx].buttons
            btn = buttons_list[row_idx][btn_idx]
            
            if field == "text":
                btn.text = value
            elif field == "type":
                btn.type = value
                if value == "url":
                    btn.callback = ""
                    btn.url = "https://..."
                else:
                    btn.url = ""
                    btn.callback = "goto_..."
            elif field == "url":
                btn.url = value
            elif field == "callback":
                btn.callback = value
                
            buttons_list[row_idx][btn_idx] = btn
            self.editor_blocks[block_idx].buttons = buttons_list