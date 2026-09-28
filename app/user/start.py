from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..database import UsersControl
from ..settings import Settings
from ..keyboards import get_user_markup

router = Router()
users = UsersControl()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """Handle the /start command.

    Registers a new user in the database if not exists and
    sends the configured start message.

    Args:
        message (Message): Incoming Telegram message.
        state (FSMContext): FSM context to reset any active states.
    """
    await state.clear()

    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    lang_code = message.from_user.language_code or ""

    settings = Settings()

    if not users.is_exists(user_id):
        users.add_user(
            user_id,
            username,
            first_name,
            last_name,
            lang_code
        )

    text = settings.get('start_text') or "Головне меню"
    await message.answer(
        text=text,
        parse_mode='HTML',
        reply_markup=get_user_markup(user_id)
    )


@router.callback_query(F.data == 'back_to_main_menu')
async def back_to_main_menu(call: CallbackQuery, state: FSMContext):
    """Handle returning to main menu from admin menu.

    Args:
        call (CallbackQuery): Incoming callback query.
        state (FSMContext): FSM context.
    """
    await state.clear()
    user_id = call.from_user.id
    settings = Settings()
    text = settings.get('start_text') or "Головне меню"

    try:
        await call.message.edit_text(
            text=text,
            parse_mode='HTML',
            reply_markup=get_user_markup(user_id)
        )
    except Exception:
        await call.message.answer(
            text=text,
            parse_mode='HTML',
            reply_markup=get_user_markup(user_id)
        )

    await call.answer()
