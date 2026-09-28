import os
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database import UsersControl, AdminsControl

router = Router()
users_control = UsersControl()
admins = AdminsControl()


class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_button_text = State()
    waiting_for_button_url = State()


def button_style_keyboard() -> InlineKeyboardMarkup:
    """Return inline keyboard for selecting button style."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔵 Синя", callback_data="btn_style_primary")],
            [InlineKeyboardButton(text="🟢 Зелена", callback_data="btn_style_success")],
            [InlineKeyboardButton(text="🔴 Червона", callback_data="btn_style_danger")],
            [InlineKeyboardButton(text="⚫ Звичайний", callback_data="btn_style_None")],
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel")]
        ]
    )


def cancel_button() -> InlineKeyboardMarkup:
    """Return a simple cancel button keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel")]
        ]
    )


def yes_no_keyboard(yes_callback: str, no_callback: str = "cancel") -> InlineKeyboardMarkup:
    """Return a Yes/No inline keyboard.

    Args:
        yes_callback (str): Callback for "Yes".
        no_callback (str): Callback for "No".

    Returns:
        InlineKeyboardMarkup: Keyboard with Yes and No buttons.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Так", callback_data=yes_callback),
                InlineKeyboardButton(text="Ні", callback_data=no_callback)
            ]
        ]
    )


def to_markdown(text: str, entities: list) -> str:
    """Convert Telegram message entities to Markdown format.

    Args:
        text (str): Original message text.
        entities (list): List of message entities.

    Returns:
        str: Markdown-formatted text.
    """
    if not entities or not text:
        return text or ""

    chars = list(text)

    for ent in sorted(entities, key=lambda e: e.offset, reverse=True):
        start = ent.offset
        end = start + ent.length
        segment = ''.join(chars[start:end])

        if ent.type == "bold":
            segment = f"*{segment}*"
        elif ent.type == "italic":
            segment = f"_{segment}_"
        elif ent.type == "underline":
            segment = f"__{segment}__"
        elif ent.type == "strikethrough":
            segment = f"~{segment}~"
        elif ent.type == "code":
            segment = f"`{segment}`"
        elif ent.type == "pre":
            segment = f"```\n{segment}\n```"
        elif ent.type == "text_link":
            segment = f"[{segment}]({ent.url})"

        chars[start:end] = list(segment)

    return ''.join(chars)


@router.callback_query(F.data == "cancel")
async def cancel_action(call: CallbackQuery, state: FSMContext):
    """Handle cancel button: remove state data and delete message."""
    await state.clear()
    await call.answer("Дію скасовано")
    try:
        await call.message.delete()
    except Exception:
        pass


@router.callback_query(F.data == "newspaper")
async def start_broadcast(call: CallbackQuery, state: FSMContext, bot: Bot):
    """Initiate broadcast creation for admins."""
    user_id = call.from_user.id

    if not admins.is_admin(user_id):
        await call.answer("❌ Ви не є адміністратором", show_alert=True)
        return

    await state.clear()

    try:
        await call.message.delete()
    except Exception:
        pass

    msg = await bot.send_message(
        chat_id=user_id,
        text="<b>✏️ Введіть текст розсилки:</b>",
        parse_mode="HTML",
        reply_markup=cancel_button()
    )

    await state.set_state(BroadcastStates.waiting_for_text)
    await state.update_data(prompt_msg_id=msg.message_id)
    await call.answer()


@router.message(BroadcastStates.waiting_for_text)
async def receive_text(message: Message, state: FSMContext, bot: Bot):
    """Receive broadcast text and ask for photo."""
    user_id = message.from_user.id
    data = await state.get_data()
    prompt_msg_id = data.get("prompt_msg_id")

    try:
        await message.delete()
    except Exception:
        pass

    # Use HTML formatting preserved from message entities
    formatted_text = message.html_text or message.text or ""
    await state.update_data(text=formatted_text)

    prompt = "<b>📸 Надішліть фото</b> або введіть <code>-</code> для пропуску."

    if prompt_msg_id:
        try:
            await bot.edit_message_text(
                text=prompt,
                chat_id=user_id,
                message_id=prompt_msg_id,
                parse_mode="HTML",
                reply_markup=cancel_button()
            )
            await state.set_state(BroadcastStates.waiting_for_photo)
            return
        except Exception:
            pass

    msg = await message.answer(
        text=prompt,
        parse_mode="HTML",
        reply_markup=cancel_button()
    )
    await state.update_data(prompt_msg_id=msg.message_id)
    await state.set_state(BroadcastStates.waiting_for_photo)


@router.message(BroadcastStates.waiting_for_photo)
async def receive_photo(message: Message, state: FSMContext, bot: Bot):
    """Receive optional broadcast photo."""
    user_id = message.from_user.id
    data = await state.get_data()
    prompt_msg_id = data.get("prompt_msg_id")

    try:
        await message.delete()
    except Exception:
        pass

    if message.text == "-":
        await state.update_data(photo_file_id=None, photo_path=None)
    elif message.photo:
        photo_file_id = message.photo[-1].file_id
        os.makedirs("app/img", exist_ok=True)
        path = "app/img/newspaper.jpg"
        try:
            await bot.download(message.photo[-1], destination=path)
        except Exception:
            pass
        await state.update_data(photo_file_id=photo_file_id, photo_path=path)
    else:
        msg = await message.answer("⚠️ Надішліть фото або '-'")
        await asyncio.sleep(2)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    prompt = "🔘 Додати кнопку до повідомлення?"
    reply_markup = yes_no_keyboard("add_button_yes", "add_button_no")

    if prompt_msg_id:
        try:
            await bot.edit_message_text(
                text=prompt,
                chat_id=user_id,
                message_id=prompt_msg_id,
                reply_markup=reply_markup
            )
            return
        except Exception:
            pass

    msg = await message.answer(
        text=prompt,
        reply_markup=reply_markup
    )
    await state.update_data(prompt_msg_id=msg.message_id)


@router.callback_query(F.data.in_({"add_button_yes", "add_button_no"}))
async def handle_button_choice(call: CallbackQuery, state: FSMContext, bot: Bot):
    """Ask user if they want to add a button to the broadcast."""
    user_id = call.from_user.id

    if call.data == "add_button_yes":
        await state.set_state(BroadcastStates.waiting_for_button_text)
        await state.update_data(prompt_msg_id=call.message.message_id)

        try:
            await call.message.edit_text(
                "<b>📝 Введіть текст кнопки:</b>",
                parse_mode="HTML",
                reply_markup=cancel_button()
            )
        except Exception:
            await call.message.answer(
                "<b>📝 Введіть текст кнопки:</b>",
                parse_mode="HTML",
                reply_markup=cancel_button()
            )
        await call.answer()
    else:
        await state.update_data(button=False)
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.answer()
        await preview_broadcast(user_id=user_id, state=state, bot=bot)


@router.message(BroadcastStates.waiting_for_button_text)
async def receive_button_text(message: Message, state: FSMContext, bot: Bot):
    """Receive the text for the broadcast button."""
    user_id = message.from_user.id
    data = await state.get_data()
    prompt_msg_id = data.get("prompt_msg_id")

    try:
        await message.delete()
    except Exception:
        pass

    button_text = message.text.strip() if message.text else ""
    await state.update_data(button_text=button_text)
    await state.set_state(BroadcastStates.waiting_for_button_url)

    prompt = "<b>🔗 Введіть посилання:</b>"

    if prompt_msg_id:
        try:
            await bot.edit_message_text(
                text=prompt,
                chat_id=user_id,
                message_id=prompt_msg_id,
                parse_mode="HTML",
                reply_markup=cancel_button()
            )
            return
        except Exception:
            pass

    msg = await message.answer(
        text=prompt,
        parse_mode="HTML",
        reply_markup=cancel_button()
    )
    await state.update_data(prompt_msg_id=msg.message_id)


@router.message(BroadcastStates.waiting_for_button_url)
async def receive_button_url(message: Message, state: FSMContext, bot: Bot):
    """Receive button URL and ask for button style."""
    user_id = message.from_user.id
    data = await state.get_data()
    prompt_msg_id = data.get("prompt_msg_id")

    try:
        await message.delete()
    except Exception:
        pass

    if prompt_msg_id:
        try:
            await bot.delete_message(chat_id=user_id, message_id=prompt_msg_id)
        except Exception:
            pass

    button_url = message.text.strip() if message.text else ""
    await state.update_data(button_url=button_url, button=True)

    msg = await message.answer(
        "<b>🎨 Оберіть стиль кнопки:</b>",
        parse_mode="HTML",
        reply_markup=button_style_keyboard()
    )
    await state.update_data(prompt_msg_id=msg.message_id)


@router.callback_query(F.data.startswith("btn_style_"))
async def handle_button_style(call: CallbackQuery, state: FSMContext, bot: Bot):
    """Handle button style selection and show preview."""
    user_id = call.from_user.id
    raw_style = call.data.replace("btn_style_", "")
    style = None if raw_style == "None" else raw_style

    await state.update_data(button_style=style, button=True)
    await call.answer("Стиль обрано")

    try:
        await call.message.delete()
    except Exception:
        pass

    await preview_broadcast(user_id=user_id, state=state, bot=bot)


async def preview_broadcast(user_id: int, state: FSMContext, bot: Bot):
    """Show preview of broadcast with optional photo and button."""
    data = await state.get_data()

    preview_buttons = []
    if data.get("button") and data.get("button_text") and data.get("button_url"):
        btn_kwargs = {
            "text": data["button_text"],
            "url": data["button_url"]
        }
        if data.get("button_style"):
            btn_kwargs["style"] = data["button_style"]

        preview_buttons.append([InlineKeyboardButton(**btn_kwargs)])

    preview_buttons.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel")])
    markup = InlineKeyboardMarkup(inline_keyboard=preview_buttons)

    broadcast_text = data.get("text", "")

    if data.get("photo_file_id"):
        await bot.send_photo(
            chat_id=user_id,
            photo=data["photo_file_id"],
            caption=broadcast_text,
            parse_mode="HTML",
            reply_markup=markup
        )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=broadcast_text,
            parse_mode="HTML",
            reply_markup=markup
        )

    count = users_control.get_users_for_stat()[0]
    confirm_msg = await bot.send_message(
        chat_id=user_id,
        text=f"<b>📬 Відправити розсилку приблизно {count} користувачам?</b>",
        parse_mode="HTML",
        reply_markup=yes_no_keyboard("send_broadcast_yes")
    )
    await state.update_data(confirm_msg_id=confirm_msg.message_id)


@router.callback_query(F.data == "send_broadcast_yes")
async def send_broadcast(call: CallbackQuery, state: FSMContext, bot: Bot):
    """Send broadcast to all users and show statistics."""
    user_id = call.from_user.id
    if not admins.is_admin(user_id):
        await call.answer("❌ Ви не є адміністратором", show_alert=True)
        return

    data = await state.get_data()
    await state.clear()

    try:
        await call.message.delete()
    except Exception:
        pass

    users_list = users_control.get_users_for_stat()[1]

    broadcast_buttons = []
    if data.get("button") and data.get("button_text") and data.get("button_url"):
        btn_kwargs = {
            "text": data["button_text"],
            "url": data["button_url"]
        }
        if data.get("button_style"):
            btn_kwargs["style"] = data["button_style"]
        broadcast_buttons.append([InlineKeyboardButton(**btn_kwargs)])

    markup = InlineKeyboardMarkup(inline_keyboard=broadcast_buttons) if broadcast_buttons else None

    success = 0
    failed = 0
    broadcast_text = data.get("text", "")
    photo_file_id = data.get("photo_file_id")

    for uid, *_ in users_list:
        try:
            if photo_file_id:
                await bot.send_photo(
                    chat_id=uid,
                    photo=photo_file_id,
                    caption=broadcast_text,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            else:
                await bot.send_message(
                    chat_id=uid,
                    text=broadcast_text,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            success += 1
            await asyncio.sleep(0.05)  # Telegram broadcast throttling
        except Exception:
            failed += 1

    await bot.send_message(
        chat_id=user_id,
        text=f"<b>Готово!</b>\n\n📨 Успішно: <b>{success}</b>\n⚠️ Помилки: <b>{failed}</b>",
        parse_mode="HTML"
    )
    await call.answer()
