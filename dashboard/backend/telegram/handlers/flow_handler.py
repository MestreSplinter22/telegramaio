# dashboard/backend/telegram/handlers/flow_handler.py

import json
import asyncio
from aiogram import Router, F, types
import reflex as rx

from dashboard.backend.telegram.common.message_handler import send_template_message
from dashboard.backend.services.payment_service import PaymentService
from dashboard.backend.telegram.utils.media_helper import MediaHelper

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
            await handle_payment_node(callback, screen_data, user_context, target_screen_key)
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

async def handle_payment_node(callback: types.CallbackQuery, node_data: dict, context: dict, target_screen_key: str):
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
    
    # --- Obter o ID da tela de pagamento atual ---
    # Este será usado para identificar de onde veio o pagamento
    payment_screen_id = target_screen_key
    
    processing_msg = await callback.message.answer("🔄 <b>Gerando QR Code PIX...</b>", parse_mode="HTML")
    
    try:
        # Chama o serviço de pagamento para processar o pagamento
        payment_service = PaymentService()
        result = payment_service.process_payment(
            amount=amount,
            gateway_name=gateway_name_preferida,
            user_context={
                "id": context["id"],
                "name": context["name"],
                "username": callback.from_user.username
            },
            success_screen_id=success_screen_id,
            payment_screen_id=payment_screen_id
        )
        
        if not result["success"]:
            await processing_msg.edit_text(f"❌ Erro: {result['error']}")
            return
        
        # Extrai os dados do pagamento
        pix_data = result["pix_data"]
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
        parse_mode = MediaHelper.detect_parse_mode(caption_text)
        # ---------------------------------------------

        if img_source:
            await processing_msg.delete()
            
            if img_source.startswith("http"):
                await callback.message.answer_photo(photo=img_source, caption=caption_text, parse_mode=parse_mode)
            else:
                # Usa o MediaHelper para converter base64 para BufferedInputFile
                try:
                    photo_file = MediaHelper.base64_to_buffered_input_file(img_source, "qrcode_pix.png")
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