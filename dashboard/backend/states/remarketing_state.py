# dashboard/backend/states/remarketing_state.py

import reflex as rx
from sqlmodel import select
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
import json
import os
from pydantic import BaseModel

from dashboard.backend.database import get_db_session
from dashboard.backend.models.transaction import Transaction
from dashboard.backend.models.user import User
from dashboard.backend.telegram.bot import bot
from dashboard.backend.telegram.common.keyboard_builder import build_keyboard
from dashboard.backend.services.payment_service import PaymentService
from dashboard.backend.telegram.utils.media_helper import MediaHelper

# Caminho do arquivo JSON
FLOWS_DIR = "dashboard/backend/telegram/flows"
REMARKETING_JSON_PATH = os.path.join(FLOWS_DIR, "remarketing.json")

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

    # --- DADOS TEMPORÁRIOS PARA O HANDLER ---
    _temp_success_data: Dict[str, Any] = {} 

    # --- EDITOR (Iniciado vazio, será carregado do JSON) ---
    editor_blocks: List[RemarketingBlock] = [
        RemarketingBlock(type="message", title="1. Mensagem de Oferta (CTA)"),
        RemarketingBlock(type="payment", title="2. Configuração do Pagamento (Pix)"),
        RemarketingBlock(type="webhook", title="3. Mensagem de Confirmação")
    ]
    
    # --- COMPUTED VARS ---
    @rx.var
    def selected_count(self) -> int:
        return len(self.selected_users)

    @rx.var
    def all_selected_checked(self) -> bool:
        return (len(self.pending_users) > 0) and (len(self.selected_users) == len(self.pending_users))

    # --- PERSISTÊNCIA JSON (NOVO) ---
    def load_configuration(self):
        """Carrega a configuração do arquivo remarketing.json para o editor."""
        if not os.path.exists(REMARKETING_JSON_PATH):
            print("⚠️ Arquivo remarketing.json não encontrado. Usando padrões.")
            # Define padrões se arquivo não existir
            self.editor_blocks[0].text = "Olá {first_name}! 🔔\n\nTemos uma oferta especial."
            self.editor_blocks[0].buttons = [[RemarketingButton(text="💳 Quero Pagar Agora", type="callback", callback="remarketing_payment")]]
            self.editor_blocks[1].text = "Pague agora seu Pix de R$ {amount}:"
            self.editor_blocks[2].text = "Pagamento Confirmado!"
            return

        try:
            with open(REMARKETING_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                screens = data.get("screens", {})

                # Mapear Nó 1: Oferta
                offer = screens.get("remarketing_offer", {})
                self.editor_blocks[0].text = offer.get("text", "")
                self.editor_blocks[0].image_url = offer.get("image_url", "")
                self.editor_blocks[0].video_url = offer.get("video_url", "")
                self.editor_blocks[0].buttons = self._parse_json_buttons(offer.get("buttons", []))

                # Mapear Nó 2: Pagamento
                payment = screens.get("remarketing_payment", {})
                self.editor_blocks[1].text = payment.get("text", "")
                self.editor_blocks[1].gateway = payment.get("gateway", "openpix")
                # amount não costuma vir no JSON estático, mas se vier, carregamos
                
                # Mapear Nó 3: Sucesso
                success = screens.get("remarketing_success", {})
                self.editor_blocks[2].text = success.get("text", "")
                self.editor_blocks[2].image_url = success.get("image_url", "")
                self.editor_blocks[2].video_url = success.get("video_url", "")
                self.editor_blocks[2].buttons = self._parse_json_buttons(success.get("buttons", []))
                
            print("✅ Configuração de remarketing carregada com sucesso.")
            self.editor_blocks = list(self.editor_blocks) # Forçar refresh UI
        except Exception as e:
            print(f"❌ Erro ao carregar remarketing.json: {e}")

    def save_configuration(self):
        """Salva o estado atual do editor no arquivo remarketing.json."""
        try:
            # Converter botões para formato JSON
            offer_btns = self._serialize_buttons(self.editor_blocks[0].buttons)
            success_btns = self._serialize_buttons(self.editor_blocks[2].buttons)

            data = {
                "screens": {
                    "remarketing_offer": {
                        "text": self.editor_blocks[0].text,
                        "image_url": self.editor_blocks[0].image_url,
                        "video_url": self.editor_blocks[0].video_url,
                        "buttons": offer_btns
                    },
                    "remarketing_payment": {
                        "type": "payment",
                        "text": self.editor_blocks[1].text,
                        "gateway": self.editor_blocks[1].gateway,
                        "webhook": "remarketing_success"
                    },
                    "remarketing_success": {
                        "type": "webhook",
                        "text": self.editor_blocks[2].text,
                        "image_url": self.editor_blocks[2].image_url,
                        "video_url": self.editor_blocks[2].video_url,
                        "buttons": success_btns
                    }
                }
            }

            os.makedirs(FLOWS_DIR, exist_ok=True)
            with open(REMARKETING_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 remarketing.json salvo com sucesso em {REMARKETING_JSON_PATH}")
        except Exception as e:
            print(f"❌ Erro ao salvar remarketing.json: {e}")

    # --- HELPER: PARSERS DE BOTÕES ---
    def _parse_json_buttons(self, json_rows: List[List[Dict]]) -> List[List[RemarketingButton]]:
        result = []
        for row in json_rows:
            new_row = []
            for btn in row:
                b_obj = RemarketingButton(text=btn.get("text", "Botão"))
                if "url" in btn:
                    b_obj.type = "url"
                    b_obj.url = btn["url"]
                elif "callback" in btn or "callback_data" in btn:
                    b_obj.type = "callback"
                    b_obj.callback = btn.get("callback") or btn.get("callback_data")
                new_row.append(b_obj)
            result.append(new_row)
        return result

    def _serialize_buttons(self, btn_rows: List[List[RemarketingButton]]) -> List[List[Dict]]:
        result = []
        for row in btn_rows:
            new_row = []
            for btn in row:
                d = {"text": btn.text}
                if btn.type == "url" and btn.url:
                    d["url"] = btn.url
                elif btn.type == "callback" and btn.callback:
                    d["callback"] = btn.callback # Usar 'callback' para compatibilidade com o fluxo
                new_row.append(d)
            if new_row:
                result.append(new_row)
        return result

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
            # ... (código existente de load users mantido) ...
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
        Envia campanha e SALVA O JSON ANTES para garantir consistência.
        """
        if not self.selected_users:
            return rx.window_alert("Selecione pelo menos um usuário.")
        
        # 1. SALVAR JSON ATUALIZADO NO DISCO
        # Isso garante que o webhook (que lê o arquivo) pegue os textos novos
        self.save_configuration()
        
        targets = [u for u in self.pending_users if u["telegram_id"] in self.selected_users]
        
        # Capturar dados para o state temporário (backup em memória)
        success_node = self.editor_blocks[2]
        success_data = {
            "text": success_node.text,
            "image_url": success_node.image_url,
            "video_url": success_node.video_url,
            "buttons": self._serialize_buttons(success_node.buttons)
        }
        self._temp_success_data = success_data
        
        msg_node = self.editor_blocks[0] # Nó de Oferta
        
        count_success = 0
        count_fail = 0
        
        for user in targets:
            try:
                ctx = {
                    "first_name": user["first_name"],
                    "amount": f"{user['raw_amount']:.2f}",
                }
                
                # Enviar Nó 1 (CTA)
                await self._send_generic_node(user["telegram_id"], msg_node, ctx)
                
                count_success += 1
                await asyncio.sleep(0.2)
                
            except Exception as e:
                print(f"Erro envio {user['telegram_id']}: {e}")
                count_fail += 1
                
        return rx.window_alert(f"Disparo concluído!\n💾 JSON Atualizado\n✅ Sucesso: {count_success}\n❌ Falhas: {count_fail}")

    async def _send_generic_node(self, chat_id, block, ctx):
        text = block.text.format(**ctx)
        markup = None
        
        if block.buttons:
            # Usar o helper de serialização para garantir formato correto
            btns_data = self._serialize_buttons(block.buttons)
            # Adaptar para o build_keyboard que espera 'callback_data'
            for row in btns_data:
                for btn in row:
                    if "callback" in btn:
                        btn["callback_data"] = btn.pop("callback")
            
            if btns_data:
                markup = build_keyboard(btns_data)

        try:
            if block.video_url:
                await bot.send_video(chat_id, video=block.video_url, caption=text, reply_markup=markup, parse_mode="HTML")
            elif block.image_url:
                await bot.send_photo(chat_id, photo=block.image_url, caption=text, reply_markup=markup, parse_mode="HTML")
            else:
                await bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode="HTML")
        except Exception as e:
            print(f"Erro no envio telegram: {e}")
            raise e

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