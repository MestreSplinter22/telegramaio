from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from dashboard.backend.models.models import User
from dashboard.backend.database import get_db_session
import logging
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)

async def get_or_create_user(telegram_id: int, username: str = None, full_name: str = None) -> User:
    from dashboard.backend.database import get_db_session
    
    session = get_db_session()
    try:
        result = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
        
        if not result:
            # Split full_name into first_name and last_name
            if full_name:
                name_parts = full_name.strip().split(' ', 1)
                first_name = name_parts[0] if name_parts else ""
                last_name = name_parts[1] if len(name_parts) > 1 else ""
            else:
                first_name = ""
                last_name = ""
            
            user = User(
                telegram_id=str(telegram_id),
                username=username or "",
                first_name=first_name,
                last_name=last_name,
                balance=0.0,
                total_spent=0.0,
                status="active",
                risk_score=0.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"New user created: {telegram_id}")
            return user
        else:
            # Update username if changed
            if username and result.username != username:
                result.username = username
            
            # Update first_name and last_name if full_name provided
            if full_name:
                name_parts = full_name.strip().split(' ', 1)
                first_name = name_parts[0] if name_parts else ""
                last_name = name_parts[1] if len(name_parts) > 1 else ""
                
                if result.first_name != first_name:
                    result.first_name = first_name
                if result.last_name != last_name:
                    result.last_name = last_name
            
            result.updated_at = datetime.utcnow()
            session.commit()
            return result
    finally:
        session.close()

@router.message(Command("start"))
async def start_command(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    
    user = await get_or_create_user(telegram_id, username, full_name)
    
    # Format the welcome message
    welcome_text = (
        f"<a href='https://i.ibb.co/rmn2VqT/akst.jpg'>👋</a> Olá <b>{full_name or 'Usuário'}</b>!\n"
        f"📢 <a href='https://t.me/akatsukicentral'>Grupo</a>\n"
        f"🧾 Seu perfil:\n"
        f"  ├👤 <b>ID:</b> <code>{telegram_id}</code>\n"
        f"  └💸 <b>Saldo:</b> R$ <b>{user.balance:.2f}</b>\n\n"
        f"🟢 <b>BÔNUS DE RECARGA ATIVO</b>\n"
        f"💸 <b>RECEBE 100% DE BÔNUS</b>\n\n"
        f"🔽 <b>VALOR MÍNIMO: R$ 50</b>"
    )
    
    # Create inline keyboard buttons
    keyboard = [
        [InlineKeyboardButton(text="AKATSUKI SHOPPING", callback_data="shopping")],
        [InlineKeyboardButton(text="ADICIONAR SALDO", callback_data="add_balance")],
        [InlineKeyboardButton(text="BOT DE PUXADA", url="https://t.me/buscasfacilbot?start=1665512795")],
        [
            InlineKeyboardButton(text="PERFIL", callback_data="profile"),
            InlineKeyboardButton(text="AJUDA", url="https://t.me/ItachiADM")
        ]
    ]
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        text=welcome_text,
        reply_markup=markup,
        parse_mode="HTML",
        disable_web_page_preview=False
    )
    
    logger.info(f"Start command executed for user: {telegram_id}")