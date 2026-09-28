from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database import AdminsControl
from app.settings import Settings

router = Router()
admins = AdminsControl()


class SettingsStates(StatesGroup):
    waiting_for_value = State()


@router.callback_query(F.data.startswith('change_value|'))
async def change_values(call: CallbackQuery, state: FSMContext):
    """Start the process of changing a setting value for admins.

    Args:
        call (CallbackQuery): Incoming callback query.
        state (FSMContext): FSM context.
    """
    user_id = call.from_user.id
    if not admins.is_admin(user_id):
        await call.answer('⚠️ У вас немає доступу.', show_alert=True)
        return

    key = call.data.split('|')[1]

    texts = {
        'start_text': (
            "📝 <b>Надішліть новий текст</b>, "
            "який буде показано при команді <code>/start</code>:"
        ),
    }

    try:
        await call.message.delete()
    except Exception:
        pass

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Скасувати зміну",
                    callback_data='cancel_cv'
                )
            ]
        ]
    )

    prompt_text = texts.get(key, "✏️ Надішліть нове значення:")
    msg = await call.bot.send_message(
        chat_id=user_id,
        text=prompt_text,
        reply_markup=markup,
        parse_mode='HTML'
    )

    await state.set_state(SettingsStates.waiting_for_value)
    await state.update_data(key=key, msg_to_del=msg.message_id)
    await call.answer()


@router.callback_query(F.data == 'cancel_cv')
async def cancel_cv(call: CallbackQuery, state: FSMContext):
    """Cancel the change value operation.

    Args:
        call (CallbackQuery): Incoming callback query.
        state (FSMContext): FSM context.
    """
    await state.clear()

    try:
        await call.message.delete()
    except Exception:
        pass

    await call.answer('❎ Зміну скасовано.', show_alert=True)


@router.message(SettingsStates.waiting_for_value)
async def change_value_final(message: Message, state: FSMContext):
    """Save the new setting value after admin input.

    Args:
        message (Message): Admin message with new value.
        state (FSMContext): FSM context.
    """
    user_id = message.from_user.id

    if not admins.is_admin(user_id):
        await state.clear()
        return

    data = await state.get_data()
    key = data.get('key')
    msg_to_del = data.get('msg_to_del')
    await state.clear()

    if not key or not message.text:
        return

    new_value = message.text.strip()
    settings = Settings()
    settings.set(key, new_value)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Повернутись до адмін-меню",
                    callback_data='admin_menu'
                )
            ]
        ]
    )

    try:
        await message.delete()
    except Exception:
        pass

    if msg_to_del:
        try:
            await message.bot.delete_message(chat_id=user_id, message_id=msg_to_del)
        except Exception:
            pass

    await message.answer(
        "✅ <b>Зміни успішно збережено!</b>\n\n",
        reply_markup=markup,
        parse_mode='HTML'
    )
