# dashboard/backend/telegram/handlers/remarketing_handler.py

from aiogram import Router, F, types
import reflex as rx
import logging

from dashboard.backend.models import Transaction
from dashboard.backend.services.payment_service import PaymentService
from dashboard.backend.telegram.utils.media_helper import MediaHelper

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "remarketing_payment")
async def handle_remarketing_payment(callback: types.CallbackQuery):
    """
    Handler que captura o clique no botão de remarketing
    e gera o PIX dinamicamente SOMENTE quando o usuário clicar.
    """
    logger.info(f"🎯 HANDLER REMARKETING CHAMADO! User: {callback.from_user.id}")
    
    user_id = str(callback.from_user.id)
    user_name = callback.from_user.first_name
    
    try:
        await callback.message.delete()
        logger.info("✅ Mensagem anterior deletada")
    except Exception as e:
        logger.error(f"❌ Erro ao deletar mensagem: {e}")
    
    # 1. Buscar transação pendente do usuário
    with rx.session() as session:
        txn = session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.status == "pending"
        ).order_by(Transaction.timestamp.desc()).first()
        
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
        
        # 3. Mensagem de processamento
        processing_msg = await callback.message.answer(
            "🔄 <b>Gerando seu QR Code PIX...</b>\n\nAguarde um momento...", 
            parse_mode="HTML"
        )
        logger.info("✅ Mensagem de processamento enviada")
        
        try:
            # 4. Gerar PIX AGORA (não antes)
            logger.info("🔄 Iniciando geração de PIX...")
            service = PaymentService()
            
            # BUSCAR DADOS DE SUCESSO DO STATE (se disponível)
            success_metadata = {}
            try:
                # Importar o state para acessar os dados temporários
                from dashboard.backend.states.remarketing_state import RemarketingState
                
                # Tentar acessar a instância do state
                # Nota: Isso é uma simplificação - em produção você pode querer salvar isso em cache/redis
                success_metadata = getattr(RemarketingState, '_temp_success_data', {})
                if success_metadata:
                    logger.info(f"✅ Dados de sucesso customizados encontrados!")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível acessar dados de sucesso: {e}")
            
            result = service.process_payment(
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
            
            logger.info(f"📋 Dados PIX: QR={bool(qr_b64)}, Copia e Cola={bool(pix_copia_cola)}")
            
            # 6. Formatar texto
            caption_text = payment_config["text"].replace("{amount}", f"{payment_config['amount']:.2f}")
            caption_text = caption_text.replace("{pix_copia_cola}", f"<code>{pix_copia_cola}</code>")
            
            # 7. Deletar mensagem de processamento
            await processing_msg.delete()
            logger.info("✅ Mensagem de processamento deletada")
            
            # 8. Enviar QR Code
            if qr_b64:
                if qr_b64.startswith("http"):
                    await callback.message.answer_photo(
                        photo=qr_b64, 
                        caption=caption_text, 
                        parse_mode="HTML"
                    )
                    logger.info("✅ QR Code enviado via URL")
                else:
                    photo_file = MediaHelper.base64_to_buffered_input_file(qr_b64, "qr.png")
                    await callback.message.answer_photo(
                        photo=photo_file, 
                        caption=caption_text, 
                        parse_mode="HTML"
                    )
                    logger.info("✅ QR Code enviado via Base64")
            else:
                await callback.message.answer(caption_text, parse_mode="HTML")
                logger.info("✅ Mensagem enviada sem QR Code")
            
            await callback.answer("✅ QR Code gerado!")
            logger.info("🎉 Processo concluído com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar PIX no remarketing: {e}", exc_info=True)
            try:
                await processing_msg.edit_text(f"⚠️ Erro ao gerar PIX: {str(e)}")
            except:
                pass
    
    await callback.answer()