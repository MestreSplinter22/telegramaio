# dashboard/backend/states/remarketing_state.py

import reflex as rx
from sqlmodel import select
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
from pydantic import BaseModel

from dashboard.backend.database import get_db_session
from dashboard.backend.models.transaction import Transaction
from dashboard.backend.models.user import User
from dashboard.backend.telegram.bot import bot
from dashboard.backend.telegram.common.keyboard_builder import build_keyboard
from dashboard.backend.services.payment_service import PaymentService
from dashboard.backend.telegram.utils.media_helper import MediaHelper

# --- MODELOS ---
class RemarketingButton(BaseModel):
    text: str = "Botão"
    type: str = "url" 
    url: str = ""
    callback: str = ""

class RemarketingBlock(BaseModel):
    type: str = "message"
    title: str = ""
    text: str = ""
    image_url: str = ""
    video_url: str = ""
    buttons: List[List[RemarketingButton]] = []
    gateway: str = "openpix"
    amount: float = 0.0

class RemarketingState(rx.State):
    # --- DADOS ---
    pending_users: List[Dict[str, Any]] = []
    loading_users: bool = False
    
    # --- SELEÇÃO ---
    selected_users: List[str] = [] 

    # --- EDITOR FIXO (3 NÓS) ---
    editor_blocks: List[RemarketingBlock] = [
        # NÓ 1: CTA 
        RemarketingBlock(
            type="message",
            title="1. Mensagem de Oferta (CTA)",
            text="Olá {first_name}! 🔔\n\nTemos uma condição especial para você finalizar seu pedido.",
            buttons=[[RemarketingButton(text="💳 Quero Pagar Agora", type="callback", callback="remarketing_payment")]]
        ),
        # NÓ 2: PAGAMENTO
        RemarketingBlock(
            type="payment",
            title="2. Configuração do Pagamento (Pix)",
            text="Aqui está seu QR Code exclusivo de R$ {amount}:",
            gateway="openpix",
            amount=0.0
        ),
        # NÓ 3: SUCESSO (A ser enviado pelo Webhook)
        RemarketingBlock(
            type="webhook",
            title="3. Mensagem de Confirmação",
            text="Pagamento confirmado! Obrigado.",
            buttons=[] 
        )
    ]
    
    # --- COMPUTED VARS ---
    @rx.var
    def selected_count(self) -> int:
        return len(self.selected_users)

    @rx.var
    def all_selected_checked(self) -> bool:
        return (len(self.pending_users) > 0) and (len(self.selected_users) == len(self.pending_users))

    # --- AÇÕES DE SELEÇÃO ---
    def toggle_all(self, checked: bool):
        if checked:
            self.selected_users = [u["telegram_id"] for u in self.pending_users]
        else:
            self.selected_users = []

    def toggle_user(self, tid: str, checked: bool):
        if checked:
            if tid not in self.selected_users:
                self.selected_users.append(tid)
        else:
            if tid in self.selected_users:
                self.selected_users.remove(tid)

    def load_pending_users(self):
        self.loading_users = True
        yield
        try:
            with get_db_session() as session:
                cutoff = datetime.utcnow() - timedelta(minutes=15)
                stmt = select(Transaction, User).where(
                    Transaction.user_id == User.telegram_id,
                    Transaction.status == "pending",
                    Transaction.timestamp < cutoff
                )
                results = session.exec(stmt).all()
                data = []
                seen = set()
                ids = []
                for txn, user in results:
                    if user.telegram_id not in seen:
                        data.append({
                            "telegram_id": user.telegram_id,
                            "first_name": user.first_name,
                            "username": user.username or "",
                            "amount": f"{txn.amount:.2f}",
                            "raw_amount": txn.amount,
                        })
                        seen.add(user.telegram_id)
                        ids.append(user.telegram_id)
                
                self.pending_users = data
                self.selected_users = ids
        finally:
            self.loading_users = False
            yield

    async def send_remarketing_campaign(self):
        """
        CORRIGIDO: Envia apenas o CTA inicial.
        O PIX será gerado quando o usuário clicar no botão via handler do bot.
        """
        if not self.selected_users:
            return rx.window_alert("Selecione pelo menos um usuário.")
        
        targets = [u for u in self.pending_users if u["telegram_id"] in self.selected_users]
        
        msg_node = self.editor_blocks[0]  # Apenas o nó de CTA
        
        count_success = 0
        count_fail = 0
        
        for user in targets:
            try:
                # Contexto para formatação
                ctx = {
                    "first_name": user["first_name"],
                    "amount": f"{user['raw_amount']:.2f}",
                }
                
                # --- ENVIAR APENAS O NÓ 1 (CTA) ---
                # O callback "remarketing_payment" será capturado pelo handler do bot
                await self._send_generic_node(user["telegram_id"], msg_node, ctx)
                
                count_success += 1
                await asyncio.sleep(0.2)
                
            except Exception as e:
                print(f"Erro envio {user['telegram_id']}: {e}")
                count_fail += 1
                
        return rx.window_alert(f"Disparo concluído!\n✅ Sucesso: {count_success}\n❌ Falhas: {count_fail}")

    async def _send_generic_node(self, chat_id, block, ctx):
        """Envia um nó genérico (mensagem com botões)"""
        text = block.text.format(**ctx)
        markup = None
        
        if block.buttons:
            raw_btns = []
            for row in block.buttons:
                raw_row = []
                for b in row:
                    btn_dict = {"text": b.text}
                    # CORREÇÃO: Usar b.callback corretamente
                    if b.type == "url" and b.url: 
                        btn_dict["url"] = b.url
                    elif b.type == "callback":
                        # O campo callback já contém o valor correto
                        btn_dict["callback_data"] = b.callback if b.callback else "noop"
                    else: 
                        btn_dict["callback_data"] = "noop"
                    raw_row.append(btn_dict)
                if raw_row: 
                    raw_btns.append(raw_row)
            if raw_btns: 
                markup = build_keyboard(raw_btns)
                print(f"🔍 DEBUG: Markup criado: {raw_btns}")  # Log para debug

        if block.video_url:
            await bot.send_video(chat_id, video=block.video_url, caption=text, reply_markup=markup, parse_mode="HTML")
        elif block.image_url:
            await bot.send_photo(chat_id, photo=block.image_url, caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode="HTML")

    # --- UPDATERS (Mantidos iguais) ---
    def update_field(self, idx: int, field: str, val: Any):
        if idx < len(self.editor_blocks):
            if field == "amount":
                try: val = float(val)
                except: val = 0.0
            setattr(self.editor_blocks[idx], field, val)
            self.editor_blocks = list(self.editor_blocks)

    def update_first_button_text(self, idx: int, val: str):
        if idx < len(self.editor_blocks) and self.editor_blocks[idx].buttons:
            self.editor_blocks[idx].buttons[0][0].text = val
            self.editor_blocks = list(self.editor_blocks)

    def set_media(self, idx: int, type: str):
        if idx < len(self.editor_blocks):
            self.editor_blocks[idx].image_url = ""
            self.editor_blocks[idx].video_url = ""
            if type == "image": self.editor_blocks[idx].image_url = "https://..."
            elif type == "video": self.editor_blocks[idx].video_url = "https://..."
            self.editor_blocks = list(self.editor_blocks)

    def add_btn_row(self, idx: int):
        self.editor_blocks[idx].buttons.append([RemarketingButton(text="Botão", url="https://...")])
        self.editor_blocks = list(self.editor_blocks)

    def add_btn(self, idx: int, r_idx: int):
        self.editor_blocks[idx].buttons[r_idx].append(RemarketingButton(text="Botão", url="https://..."))
        self.editor_blocks = list(self.editor_blocks)

    def remove_btn(self, idx: int, r_idx: int, b_idx: int):
        row = self.editor_blocks[idx].buttons[r_idx]
        if b_idx < len(row):
            row.pop(b_idx)
            if not row: self.editor_blocks[idx].buttons.pop(r_idx)
            self.editor_blocks = list(self.editor_blocks)

    def update_btn(self, idx: int, r_idx: int, b_idx: int, field: str, val: str):
        b = self.editor_blocks[idx].buttons[r_idx][b_idx]
        setattr(b, field, val)
        self.editor_blocks = list(self.editor_blocks)