from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database import AdminsControl

router = Router()
admins = AdminsControl()


class AdminControlStates(StatesGroup):
    waiting_for_admin_id = State()


def get_cancel_markup(callback: str = 'admin_menu') -> InlineKeyboardMarkup:
    """Create a simple cancel button inline keyboard.

    Args:
        callback (str): Callback data for the cancel button.

    Returns:
        InlineKeyboardMarkup: Keyboard with a single cancel button.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='❌ Скасувати', callback_data=callback)]
        ]
    )


@router.callback_query(F.data == 'admins_control')
async def admins_control(call: CallbackQuery, state: FSMContext):
    """Show admin management options to authorized users.

    Args:
        call (CallbackQuery): Incoming callback query.
        state (FSMContext): FSM context.
    """
    user_id = call.from_user.id
    await state.clear()

    if not admins.is_admin(user_id):
        await call.answer(
            '⚠️ У вас немає доступу до цієї функції.',
            show_alert=True
        )
        return

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='➕ Додати адміністратора',
                    callback_data='c_admins|add'
                ),
                InlineKeyboardButton(
                    text='➖ Видалити адміністратора',
                    callback_data='c_admins|del'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🔙 Повернутись',
                    callback_data='admin_menu'
                )
            ]
        ]
    )

    try:
        await call.message.edit_text(
            "<b>⚙️ Управління адміністраторами</b>\n"
            "Оберіть дію, яку бажаєте виконати:",
            reply_markup=markup,
            parse_mode='HTML'
        )
    except Exception:
        await call.message.answer(
            "<b>⚙️ Управління адміністраторами</b>\n"
            "Оберіть дію, яку бажаєте виконати:",
            reply_markup=markup,
            parse_mode='HTML'
        )

    await call.answer()


@router.callback_query(F.data.startswith('c_admins|'))
async def actions_control(call: CallbackQuery, state: FSMContext):
    """Handle add or delete admin actions.

    Args:
        call (CallbackQuery): Incoming callback query.
        state (FSMContext): FSM context.
    """
    user_id = call.from_user.id

    if not admins.is_admin(user_id):
        await call.answer(
            '⚠️ У вас немає доступу до цієї функції.',
            show_alert=True
        )
        return

    action = call.data.split('|')[1]

    if action == 'add':
        await state.set_state(AdminControlStates.waiting_for_admin_id)
        markup = get_cancel_markup('admin_menu')
        try:
            await call.message.edit_text(
                '🆔 Введіть <b>ID нового адміністратора</b>:',
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception:
            await call.message.answer(
                '🆔 Введіть <b>ID нового адміністратора</b>:',
                parse_mode='HTML',
                reply_markup=markup
            )
        await call.answer()

    elif action == 'del':
        await state.clear()
        all_admins = admins.get_admins()
        if not all_admins:
            await call.answer(
                '⚠️ Наразі немає доданих адміністраторів.',
                show_alert=True
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    text=f'🆔 {admin_id}',
                    callback_data=f'delete_admin|{admin_id}'
                )
            ]
            for admin_id in all_admins
        ]
        keyboard.append([
            InlineKeyboardButton(
                text='🔙 Повернутись',
                callback_data='admin_menu'
            )
        ])
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        try:
            await call.message.edit_text(
                '<b>Оберіть адміністратора, якого бажаєте видалити:</b>',
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception:
            await call.message.answer(
                '<b>Оберіть адміністратора, якого бажаєте видалити:</b>',
                parse_mode='HTML',
                reply_markup=markup
            )
        await call.answer()


@router.callback_query(F.data.startswith('delete_admin|'))
async def delete_admin(call: CallbackQuery):
    """Delete an admin and update the list.

    Args:
        call (CallbackQuery): Incoming callback query.
    """
    user_id = call.from_user.id
    try:
        admin_id = int(call.data.split('|')[1])
    except (ValueError, IndexError):
        await call.answer('❌ Некоректний ID.', show_alert=True)
        return

    if not admins.is_admin(user_id):
        await call.answer(
            '⚠️ У вас немає доступу до цієї функції.',
            show_alert=True
        )
        return

    admins.del_admin(admin_id)
    all_admins = admins.get_admins()

    keyboard = [
        [
            InlineKeyboardButton(
                text=f'🆔 {adm}',
                callback_data=f'delete_admin|{adm}'
            )
        ]
        for adm in all_admins
    ]
    keyboard.append([
        InlineKeyboardButton(
            text='🔙 Повернутись',
            callback_data='admin_menu'
        )
    ])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await call.answer(
        f'✅ Адміністратора {admin_id} видалено успішно.',
        show_alert=True
    )

    try:
        await call.message.edit_text(
            '<b>Оберіть адміністратора, якого бажаєте видалити:</b>',
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception:
        await call.message.answer(
            '<b>Оберіть адміністратора, якого бажаєте видалити:</b>',
            parse_mode='HTML',
            reply_markup=markup
        )


@router.message(AdminControlStates.waiting_for_admin_id)
async def process_add_admin_id(message: Message, state: FSMContext):
    """Process adding a new admin by ID.

    Args:
        message (Message): Incoming message with new admin ID.
        state (FSMContext): FSM context.
    """
    user_id = message.from_user.id

    if not admins.is_admin(user_id):
        await state.clear()
        return

    new_admin_id = (message.text or "").strip()

    if not new_admin_id.isdigit():
        await message.answer(
            '⚠️ ID повинен бути числом. Спробуйте ще раз:',
            reply_markup=get_cancel_markup('admin_menu')
        )
        return

    await state.clear()
    new_admin_id_int = int(new_admin_id)
    added = admins.add_admin(new_admin_id_int, 'external')

    back_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔙 Повернутись',
                    callback_data='admin_menu'
                )
            ]
        ]
    )

    if added:
        await message.answer(
            f'✅ Адміністратора з ID <code>{new_admin_id_int}</code> додано успішно.',
            parse_mode='HTML',
            reply_markup=back_markup
        )
    else:
        await message.answer(
            f'⚠️ Адміністратор з ID <code>{new_admin_id_int}</code> вже існує або сталася помилка.',
            parse_mode='HTML',
            reply_markup=back_markup
        )
