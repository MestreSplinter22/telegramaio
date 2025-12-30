# dashboard/backend/telegram/handlers/flow_handler.py

import json
import asyncio
import base64
import uuid
from aiogram import Router, F, types
from aiogram.types import BufferedInputFile
import reflex as rx

from dashboard.backend.telegram.common.message_handler import send_template_message
from dashboard.backend.models.models import GatewayConfig, User, Transaction
from dashboard.backend.gateways.efi_service import EfiPixService
from dashboard.backend.gateways.suitpay_service import SuitPayService
from dashboard.backend.gateways.openpix_service import OpenPixService

router = Router()

def load_flow_screens_fresh():
    path = "dashboard/backend/telegram/flows/start_flow.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("screens", {})
    except Exception as e:
        print(f"Erro ao carregar flow: {e}")
        return {}

@router.callback_query(F.data.startswith("goto_"))
async def navigation_handler(callback: types.CallbackQuery):
    target_screen_key = callback.data.replace("goto_", "")
    screens = load_flow_screens_fresh()
    
    if target_screen_key in screens:
        screen_data = screens[target_screen_key]
        user_context = {
            "name": callback.from_user.first_name,
            "id": callback.from_user.id
        }
        
        try:
            await callback.message.delete()
        except Exception:
            pass 

        if isinstance(screen_data, dict) and screen_data.get("type") == "payment":
            await handle_payment_node(callback, screen_data, user_context)
            return

        if isinstance(screen_data, list):
            for part in screen_data:
                await send_template_message(callback.message, part, context=user_context)
                await asyncio.sleep(0.3)
        else:
            await send_template_message(callback.message, screen_data, context=user_context)
    else:
        await callback.answer("Opção indisponível.", show_alert=True)
    
    await callback.answer()

async def handle_payment_node(callback: types.CallbackQuery, node_data: dict, context: dict):
    amount = float(node_data.get("amount", 10.00))
    gateway_name_preferida = node_data.get("gateway") 
    
    # --- Extração do ID da tela de sucesso ---
    success_screen_id = None
    if "on_success" in node_data:
        success_screen_id = node_data["on_success"]
    
    # Fallback: tenta pegar do botão se não tiver definido explicitamente
    if not success_screen_id and "buttons" in node_data and node_data["buttons"]:
        try:
            first_btn = node_data["buttons"][0][0]
            cb = first_btn.get("callback", "")
            if cb.startswith("goto_"):
                success_screen_id = cb.replace("goto_", "")
        except Exception:
            pass
    
    processing_msg = await callback.message.answer("🔄 <b>Gerando QR Code PIX...</b>", parse_mode="HTML")
    
    try:
        with rx.session() as session:
            # 1. Busca Gateway
            query = session.query(GatewayConfig).filter(GatewayConfig.is_active == True)
            if gateway_name_preferida:
                gateway = query.filter(GatewayConfig.name == gateway_name_preferida).first()
            else:
                gateway = query.first()
            
            if not gateway:
                gateway = session.query(GatewayConfig).filter(GatewayConfig.is_active == True).first()
                if not gateway:
                    await processing_msg.edit_text("❌ Erro: Nenhuma gateway ativa.")
                    return

            # 2. Usuário
            user = session.query(User).filter(User.telegram_id == str(context["id"])).first()
            if not user:
                user = User(
                    telegram_id=str(context["id"]),
                    username=callback.from_user.username or "SemUser",
                    first_name=context["name"],
                    last_name=""
                )
                session.add(user)
                session.commit()

            # 3. Gerar PIX
            txid = uuid.uuid4().hex
            pix_data = {}
            nome_pagador = context["name"]
            
            if gateway.name == "efi_bank":
                service = EfiPixService(gateway)
                efi_resp = service.create_immediate_charge(
                    txid=txid,
                    cpf="12345678909" if gateway.is_sandbox else "00000000000",
                    nome=nome_pagador,
                    valor=f"{amount:.2f}"
                )
                pix_data = {
                    "pix_copia_cola": efi_resp.get("qrcode") or efi_resp.get("pixCopiaECola"),
                    "qrcode_base64": efi_resp.get("imagemQrcode"),
                    "external_id": txid
                }
                
            elif gateway.name == "suitpay":
                service = SuitPayService(gateway)
                suit_resp = service.create_pix_payment(
                    txid=txid,
                    cpf="00000000000",
                    nome=nome_pagador,
                    email="cliente@email.com",
                    valor=amount
                )
                pix_data = {
                    "pix_copia_cola": suit_resp.get("pix_copia_cola"),
                    "qrcode_base64": suit_resp.get("qrcode_base64"),
                    "external_id": suit_resp.get("txid")
                }

            elif gateway.name == "openpix":
                service = OpenPixService(gateway)
                op_resp = service.create_charge(
                    txid=txid,
                    nome=nome_pagador,
                    cpf=None, 
                    valor=amount,
                    email="cliente@sememail.com"
                )
                pix_data = {
                    "pix_copia_cola": op_resp.get("pix_copia_cola"),
                    "qrcode_base64": op_resp.get("qrcode_base64"),
                    "external_id": op_resp.get("txid")
                }

            # 4. Salvar Transação
            extra_data_payload = {
                "txid": txid, 
                "gateway_id": gateway.id, 
                "external_id": pix_data.get("external_id")
            }
            
            # --- PADRONIZAÇÃO: Salvamos como success_screen_id ---
            if success_screen_id:
                extra_data_payload["success_screen_id"] = success_screen_id

            new_txn = Transaction(
                user_id=str(user.id),
                type="deposit",
                amount=amount,
                description=f"Recarga via {gateway.name}",
                status="pending",
                extra_data=json.dumps(extra_data_payload)
            )
            session.add(new_txn)
            session.commit()

            # 5. Enviar Resposta Visual (CORRIGIDO PARA USAR TEXTO DO JSON)
            img_source = pix_data.get("qrcode_base64")
            copia_e_cola = pix_data.get("pix_copia_cola")
            
            # --- AQUI ESTA A CORREÇÃO DA MENSAGEM 1 ---
            # Pega o texto do nó (definido no FlowBuilder)
            raw_text = node_data.get("text", "✅ Pagamento Gerado! Use o QR Code abaixo.")
            
            # Faz as substituições de variáveis
            caption_text = raw_text.replace("{pix_copia_cola}", copia_e_cola or "") \
                                   .replace("{amount}", f"{amount:.2f}") \
                                   .replace("{valor}", f"{amount:.2f}")
            
            # Detecta se usa Markdown ou HTML
            parse_mode = "Markdown" if "*" in caption_text else "HTML"
            # ---------------------------------------------

            if img_source:
                await processing_msg.delete()
                
                if img_source.startswith("http"):
                    await callback.message.answer_photo(photo=img_source, caption=caption_text, parse_mode=parse_mode)
                else:
                    if "," in img_source: img_source = img_source.split(",")[1]
                    img_source = img_source.strip().replace("\n", "").replace("\r", "")
                    try:
                        img_bytes = base64.b64decode(img_source)
                        photo_file = BufferedInputFile(img_bytes, filename="qrcode_pix.png")
                        await callback.message.answer_photo(photo=photo_file, caption=caption_text, parse_mode=parse_mode)
                    except Exception:
                        await callback.message.answer(caption_text, parse_mode=parse_mode)
            else:
                await processing_msg.edit_text(caption_text, parse_mode=parse_mode)

            # Se o texto principal não tiver o copia e cola, mandamos separado
            if copia_e_cola and "{pix_copia_cola}" not in raw_text:
                await callback.message.answer(f"<code>{copia_e_cola}</code>", parse_mode="HTML")

    except Exception as e:
        print(f"Erro no handler de pagamento: {e}")
        try:
            await processing_msg.edit_text(f"⚠️ Erro ao gerar PIX: {str(e)}")
        except:
            pass