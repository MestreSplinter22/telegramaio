# dashboard/backend/telegram/handlers/remarketing_handler.py

from aiogram import Router, F, types
import reflex as rx
import logging
import json
import os
import asyncio

from dashboard.backend.models import Transaction
from dashboard.backend.services.payment_service import PaymentService
from dashboard.backend.telegram.utils.media_helper import MediaHelper

router = Router()
logger = logging.getLogger(__name__)

# Definir caminho do arquivo de fluxo do remarketing
FLOWS_DIR = "dashboard/backend/telegram/flows"
REMARKETING_FLOW_FILE = os.path.join(FLOWS_DIR, "remarketing.json")

def _get_pending_transaction(user_id: str):
    """Helper síncrono para buscar transação no DB."""
    with rx.session() as session:
        return session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.status == "pending"
        ).order_by(Transaction.timestamp.desc()).first()

def _save_remarketing_nodes(nodes: dict):
    """Helper síncrono para salvar JSON."""
    try:
        os.makedirs(FLOWS_DIR, exist_ok=True)
        with open(REMARKETING_FLOW_FILE, "w", encoding="utf-8") as f:
            json.dump(nodes, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Nós de remarketing salvos em: {REMARKETING_FLOW_FILE}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar JSON de remarketing: {e}")

@router.callback_query(F.data == "remarketing_payment")
async def handle_remarketing_payment(callback: types.CallbackQuery):
    """
    Handler que captura o clique no botão de remarketing
    e gera o PIX dinamicamente (versão Async).
    """
    logger.info(f"🎯 HANDLER REMARKETING CHAMADO! User: {callback.from_user.id}")
    
    user_id = str(callback.from_user.id)
    user_name = callback.from_user.first_name
    
    try:
        await callback.message.delete()
        logger.info("✅ Mensagem anterior deletada")
    except Exception as e:
        logger.error(f"❌ Erro ao deletar mensagem: {e}")
    
    # 1. Buscar transação pendente do usuário (Offload para Thread)
    txn = await asyncio.to_thread(_get_pending_transaction, user_id)
        
    if not txn:
        logger.warning(f"⚠️ Nenhuma transação pendente para user {user_id}")
        await callback.answer("Nenhuma transação pendente encontrada.", show_alert=True)
        return
    
    logger.info(f"✅ Transação encontrada: ID={txn.id}, Amount={txn.amount}")
    
    # 2. Configuração do pagamento
    payment_config = {
        "gateway": "openpix",
        "amount": txn.amount,
        "text": "💳 <b>Pagamento Gerado!</b>\n\nAqui está seu QR Code de R$ {amount}:\n\n{pix_copia_cola}"
    }

    # --- NOVO: SALVAR OS 3 NÓS NO ARQUIVO JSON (Offload para Thread) ---
    remarketing_nodes = {
        "screens": {
            "remarketing_offer": {
                "text": "Oferta Especial de Remarketing", 
                "buttons": [[{"text": "💳 Quero Pagar Agora", "callback": "remarketing_payment"}]]
            },
            "remarketing_payment": {
                "type": "payment",
                "text": payment_config["text"], # Salva o texto configurado dinamicamente
                "gateway": "openpix",
                "webhook": "remarketing_success"
            },
            "remarketing_success": {
                "type": "webhook",
                "text": "✅ <b>Pagamento de Remarketing Confirmado!</b>\n\n🎉 Parabéns <b>{first_name}</b>!\nRecebemos seu pagamento de R$ {amount}.\n\nSeu acesso/crédito foi liberado.",
                "buttons": [
                    [{"text": "🚀 Acessar Grupo VIP", "url": "https://t.me/+D6_NwSvlSdI1M2Vh"}]
                ]
            }
        }
    }
    
    await asyncio.to_thread(_save_remarketing_nodes, remarketing_nodes)
    # -----------------------------------------------
    
    # 3. Mensagem de processamento
    processing_msg = await callback.message.answer(
        "🔄 <b>Gerando seu QR Code PIX...</b>\n\nAguarde um momento...", 
        parse_mode="HTML"
    )
    logger.info("✅ Mensagem de processamento enviada")
    
    try:
        # 4. Gerar PIX AGORA (ASYNC)
        logger.info("🔄 Iniciando geração de PIX (Async)...")
        service = PaymentService()
        
        # Tentar buscar metadados extras se disponíveis
        success_metadata = {}
        try:
            from dashboard.backend.states.remarketing_state import RemarketingState
            # NOTA: Acessar variável de classe ainda é arriscado em multi-processos/threads, 
            # mas não bloqueia o IO.
            success_metadata = getattr(RemarketingState, '_temp_success_data', {})
        except:
            pass
        
        # CHAMADA ASSÍNCRONA
        result = await service.process_payment_async(
            amount=payment_config["amount"],
            gateway_name=payment_config["gateway"],
            user_context={
                "id": int(user_id),
                "name": user_name,
                "username": callback.from_user.username or "user"
            },
            payment_screen_id="remarketing_payment", 
            success_screen_id="remarketing_success", 
            extra_metadata={"remarketing_success_data": success_metadata} if success_metadata else None
        )
        
        if not result["success"]:
            logger.error(f"❌ Erro ao gerar PIX: {result.get('error')}")
            await processing_msg.edit_text(f"❌ Erro: {result['error']}")
            return
        
        logger.info("✅ PIX gerado com sucesso!")
        
        # 5. Extrair dados do PIX
        pix_data = result["pix_data"]
        qr_b64 = pix_data.get("qrcode_base64", "")
        pix_copia_cola = pix_data.get("pix_copia_cola", "")
        
        # 6. Formatar texto usando o config
        caption_text = payment_config["text"].replace("{amount}", f"{payment_config['amount']:.2f}")
        caption_text = caption_text.replace("{pix_copia_cola}", f"<code>{pix_copia_cola}</code>")
        
        # 7. Deletar mensagem de processamento
        await processing_msg.delete()
        
        # 8. Enviar QR Code
        if qr_b64:
            if qr_b64.startswith("http"):
                await callback.message.answer_photo(photo=qr_b64, caption=caption_text, parse_mode="HTML")
            else:
                # MediaHelper pode bloquear se fizer IO pesado, mas conversão b64 é rápida.
                # Se base64_to_buffered_input_file for pesado, mover para thread.
                photo_file = await asyncio.to_thread(MediaHelper.base64_to_buffered_input_file, qr_b64, "qr.png")
                await callback.message.answer_photo(photo=photo_file, caption=caption_text, parse_mode="HTML")
        else:
            await callback.message.answer(caption_text, parse_mode="HTML")
        
        await callback.answer("✅ QR Code gerado!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar PIX no remarketing: {e}", exc_info=True)
        try:
            await processing_msg.edit_text(f"⚠️ Erro ao gerar PIX: {str(e)}")
        except:
            pass
    
    await callback.answer()