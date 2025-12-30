# dashboard/backend/telegram/handlers/flow_handler.py

import json
import asyncio
import base64
import uuid
import re  # Import necessário para limpar o base64
from aiogram import Router, F, types
from aiogram.types import BufferedInputFile
import reflex as rx

from dashboard.backend.telegram.common.message_handler import send_template_message
from dashboard.backend.models.models import GatewayConfig, User, Transaction
from dashboard.backend.gateways.efi_service import EfiPixService
from dashboard.backend.gateways.suitpay_service import SuitPayService
from dashboard.backend.gateways.openpix_service import OpenPixService

router = Router()

def load_flow_screens():
    path = "dashboard/backend/telegram/flows/start_flow.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["screens"]

@router.callback_query(F.data.startswith("goto_"))
async def navigation_handler(callback: types.CallbackQuery):
    target_screen_key = callback.data.replace("goto_", "")
    screens = load_flow_screens()
    
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
    # Se não especificar gateway, o sistema buscará a ativa no banco automaticamente
    gateway_name_preferida = node_data.get("gateway") 
    
    processing_msg = await callback.message.answer("🔄 <b>Gerando QR Code PIX...</b>", parse_mode="HTML")
    
    try:
        with rx.session() as session:
            # 1. Lógica de Seleção de Gateway
            query = session.query(GatewayConfig).filter(GatewayConfig.is_active == True)
            
            if gateway_name_preferida:
                gateway = query.filter(GatewayConfig.name == gateway_name_preferida).first()
            else:
                gateway = query.first()
            
            if not gateway:
                # Tenta fallback para qualquer uma ativa
                gateway = session.query(GatewayConfig).filter(GatewayConfig.is_active == True).first()
                if not gateway:
                    await processing_msg.edit_text("❌ Erro: Nenhuma gateway de pagamento ativa.")
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
            
            # Formata dados do cliente
            cpf_user = "12345678909" # Em prod: user.cpf
            email_user = "cliente@email.com"

            if gateway.name == "efi_bank":
                service = EfiPixService(gateway)
                efi_resp = service.create_immediate_charge(
                    txid=txid,
                    cpf=cpf_user, 
                    nome=context["name"],
                    valor=f"{amount:.2f}"
                )
                # Normalização
                pix_data = {
                    "pix_copia_cola": efi_resp.get("qrcode") or efi_resp.get("pixCopiaECola"),
                    "qrcode_base64": efi_resp.get("imagemQrcode"),
                    "external_id": txid
                }
                
            elif gateway.name == "suitpay":
                service = SuitPayService(gateway)
                suit_resp = service.create_pix_payment(
                    txid=txid,
                    cpf=cpf_user,
                    nome=context["name"],
                    email=email_user,
                    valor=amount
                )
                pix_data = {
                    "pix_copia_cola": suit_resp.get("pix_copia_cola"),
                    "qrcode_base64": suit_resp.get("qrcode_base64"),
                    "external_id": suit_resp.get("txid")
                }

            elif gateway.name == "openpix": # <--- BLOCO NOVO
                service = OpenPixService(gateway)
                
                op_resp = service.create_charge(
                    txid=txid,
                    nome=context["name"],
                    cpf=cpf_user,
                    valor=amount
                )
                pix_data = {
                    "pix_copia_cola": op_resp.get("pix_copia_cola"),
                    "qrcode_base64": op_resp.get("qrcode_base64"),
                    "external_id": op_resp.get("txid")
                }

            # 4. Salvar Transação
            new_txn = Transaction(
                user_id=str(user.id),
                type="deposit",
                amount=amount,
                description=f"Recarga via {gateway.name}",
                status="pending",
                extra_data=json.dumps({
                    "txid": txid, 
                    "gateway_id": gateway.id,
                    "external_id": pix_data["external_id"]
                })
            )
            session.add(new_txn)
            session.commit()

# 5. Enviar Resposta Visual
            img_source = pix_data.get("qrcode_base64")
            
            if img_source:
                await processing_msg.delete()
                
                # CENÁRIO A: É um Link/URL (Comum na OpenPix)
                if img_source.startswith("http"):
                    await callback.message.answer_photo(
                        photo=img_source,
                        caption=f"✅ <b>Pagamento Gerado!</b>\n\nGateway: {gateway.name}\n💰 Valor: <b>R$ {amount:.2f}</b>\n\nEscaneie o QR Code ou use o código abaixo:",
                        parse_mode="HTML"
                    )
                
                # CENÁRIO B: É Base64 (Comum na Efí/SuitPay)
                else:
                    # Limpeza do Base64
                    if "," in img_source:
                        img_source = img_source.split(",")[1]
                    img_source = img_source.strip().replace("\n", "").replace("\r", "")

                    try:
                        img_bytes = base64.b64decode(img_source)
                        photo_file = BufferedInputFile(img_bytes, filename="qrcode_pix.png")

                        await callback.message.answer_photo(
                            photo=photo_file,
                            caption=f"✅ <b>Pagamento Gerado!</b>\n\nGateway: {gateway.name}\n💰 Valor: <b>R$ {amount:.2f}</b>\n\nEscaneie o QR Code ou use o código abaixo:",
                            parse_mode="HTML"
                        )
                    except Exception as e_img:
                        print(f"Erro decodificando imagem: {e_img}")
                        await callback.message.answer("⚠️ QR Code gerado, mas erro ao exibir a imagem. Use o código copia e cola abaixo.")
            else:
                await processing_msg.edit_text("⚠️ QR Code gerado, mas sem imagem disponível.")

    except Exception as e:
        print(f"Erro no handler de pagamento: {e}")
        try:
            await processing_msg.edit_text(f"⚠️ Erro ao gerar PIX: {str(e)}")
        except:
            pass