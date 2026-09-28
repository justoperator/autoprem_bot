from html import escape
from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from app.database import UsersControl, AdminsControl

router = Router()
users = UsersControl()
admins = AdminsControl()


def escape_html(text: str) -> str:
    """Escape text for HTML or return a placeholder if empty.

    Args:
        text (str): Input text.

    Returns:
        str: Escaped text or "Невідомо" if empty.
    """
    return escape(str(text)) if text else "Невідомо"


@router.callback_query(F.data == 'view_stats')
async def view_stats(call: CallbackQuery):
    """Display general bot user statistics to admins.

    Args:
        call (CallbackQuery): Callback from admin.
    """
    admin_id = call.from_user.id

    if not admins.is_admin(admin_id):
        await call.answer('⚠️ У вас немає доступу.', show_alert=True)
        return

    count, all_users, count_last_week, count_last_month = users.get_users_for_stat()

    stat_message = (
        f"<b>📊 Статистика користувачів бота</b>\n\n"
        f"👥 Загальна кількість користувачів: <b>{count}</b>\n\n"
        f"🗓️ За останній тиждень: {count_last_week}\n"
        f"🗓️ За останній місяць: {count_last_month}\n\n"
        f"<b>Список користувачів:</b>"
    )

    keyboard = []
    for user_id, first_name, reg_date in all_users:
        username_safe = escape_html(first_name)
        reg_date_safe = escape_html(reg_date)
        keyboard.append([
            InlineKeyboardButton(
                text=f"{username_safe} • {reg_date_safe}",
                callback_data=f"show_full_info|{user_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text='🔙 Повернутись',
            callback_data='admin_menu'
        )
    ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    try:
        await call.message.edit_text(
            stat_message,
            reply_markup=markup,
            parse_mode='HTML'
        )
    except Exception:
        await call.message.answer(
            stat_message,
            reply_markup=markup,
            parse_mode='HTML'
        )

    await call.answer()


@router.callback_query(F.data.startswith('show_full_info|'))
async def show_full_info(call: CallbackQuery):
    """Display detailed information for a selected user.

    Args:
        call (CallbackQuery): Callback from admin.
    """
    admin_id = call.from_user.id

    if not admins.is_admin(admin_id):
        await call.answer('⚠️ У вас немає доступу.', show_alert=True)
        return

    try:
        target_user_id = int(call.data.split('|')[1])
    except (ValueError, IndexError):
        await call.answer('❌ Некоректний ID користувача.', show_alert=True)
        return

    user_info = users.get_user_for_stat(target_user_id)

    if not user_info:
        await call.answer("❌ Користувач не знайдений", show_alert=True)
        return

    user_id, username, first_name, last_name, reg_date, lang_code = user_info

    info_message = (
        f"<b>👤 Повна інформація про користувача</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Username: @{escape_html(username)}\n"
        f"📝 Ім'я: <code>{escape_html(first_name)}</code>\n"
        f"📛 Прізвище: <code>{escape_html(last_name)}</code>\n"
        f"🗓️ Дата реєстрації: <code>{escape_html(reg_date)}</code>\n"
        f"🌐 Мова: <code>{escape_html(lang_code)}</code>\n"
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔙 Повернутись',
                    callback_data='view_stats'
                )
            ]
        ]
    )

    try:
        await call.message.edit_text(
            info_message,
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception:
        await call.message.answer(
            info_message,
            parse_mode='HTML',
            reply_markup=markup
        )

    await call.answer()
