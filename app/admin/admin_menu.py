from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards import get_admin_menu
from app.database import AdminsControl

router = Router()
admins = AdminsControl()


@router.callback_query(F.data.in_({'admin_menu', 'admi_menu'}))
async def admin_menu(call: CallbackQuery, state: FSMContext):
    """Handle admin menu callback query.

    Checks if the user has admin rights. If authorized,
    edits the message and shows the admin menu keyboard.
    Otherwise, displays an access denied alert.

    Args:
        call (CallbackQuery): Incoming callback query.
        state (FSMContext): FSM context to clear active steps.
    """
    user_id = call.from_user.id
    await state.clear()

    if not admins.is_admin(user_id):
        await call.answer(
            '⚠️ Наразі у вас немає доступу до цієї функції.',
            show_alert=True
        )
        return

    markup = get_admin_menu()

    try:
        await call.message.edit_text(
            "<b>⚙️ Адмін-меню</b>\n"
            "Оберіть дію, яку бажаєте виконати:",
            reply_markup=markup,
            parse_mode='HTML'
        )
    except Exception:
        await call.message.answer(
            "<b>⚙️ Адмін-меню</b>\n"
            "Оберіть дію, яку бажаєте виконати:",
            reply_markup=markup,
            parse_mode='HTML'
        )

    await call.answer()
