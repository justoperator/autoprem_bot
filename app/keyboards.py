from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .database import AdminsControl

admins = AdminsControl()


def get_admin_menu() -> InlineKeyboardMarkup:
    """Create inline keyboard markup for the admin menu.

    Returns:
        InlineKeyboardMarkup: Configured inline keyboard with
        admin control buttons.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🛠 Управління адмінами', callback_data='admins_control')],
            [InlineKeyboardButton(text='💬 Розсилка', callback_data='newspaper')],
            [InlineKeyboardButton(text='📊 Статистика користувачів', callback_data='view_stats')],
            [InlineKeyboardButton(text='📝 Змінити стартовий текст', callback_data='change_value|start_text')],
            [InlineKeyboardButton(text='🔙 Повернутись', callback_data='back_to_main_menu')],
        ]
    )


def get_user_markup(user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard markup for user menu.

    Args:
        user_id (int): Telegram user ID.

    Returns:
        InlineKeyboardMarkup: User menu with admin button if authorized.
    """
    keyboard = []
    if admins.is_admin(user_id):
        keyboard.append([
            InlineKeyboardButton(
                text='⚙ Адмін-меню',
                callback_data='admin_menu'
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)