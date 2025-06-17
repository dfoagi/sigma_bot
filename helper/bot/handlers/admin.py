import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from helper.bot.moderation import block_user, unblock_user
from helper.core.model_state import get_current_model, set_current_model
from config import ADMIN_ID

admin_router = Router()


class SetModelState(StatesGroup):
    choosing = State()


AVAILABLE_MODELS = [
    "gpt-4.1-mini-2025-04-14",
    "o4-mini-2025-04-16",
    "gpt-4.1-2025-04-14",
    "gpt-4o-2024-08-06",
    "claude-3-haiku-20240307",
    "claude-3-5-haiku-20241022",
    "claude-3-7-sonnet-20250219",
    "claude-sonnet-4-20250514",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-pro-preview-06-05"
]

MODEL_PRICE = {"gpt-4.1-mini-2025-04-14": "0.5₽",
    "o4-mini-2025-04-16": "2.1₽",
    "gpt-4.1-2025-04-14": "2.75₽",
    "gpt-4o-2024-08-06": "2.7₽",
    "claude-3-haiku-20240307": "0.41₽",
    "claude-3-5-haiku-20241022": "1.7₽",
    "claude-3-7-sonnet-20250219": "5.5₽",
    "claude-sonnet-4-20250514": "5.8₽",
    "gemini-2.5-flash-preview-05-20": "0.05₽",
    "gemini-2.5-pro-preview-06-05": "2.6₽"}


@admin_router.message(Command("set_model"))
async def start_set_model(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    builder = InlineKeyboardBuilder()
    for model in AVAILABLE_MODELS:
        builder.button(text=model + ' ' + MODEL_PRICE[model], callback_data=f"model:{model}")
    builder.button(text="❌ Отмена", callback_data="model:cancel")
    builder.adjust(1)

    cur_model = get_current_model()

    await message.answer(f"Сейчас выбрана {cur_model} \n Выберите модель:", reply_markup=builder.as_markup())
    await state.set_state(SetModelState.choosing)


@admin_router.callback_query(F.data.startswith("model:"))
async def model_chosen(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("⛔ Недостаточно прав.", show_alert=True)

    model = callback.data.split(":", 1)[1]

    if model == "cancel":
        await callback.message.edit_text("❌ Выбор модели отменён.")
        await state.clear()
        return
    
    set_current_model(model)
    await callback.message.edit_text(f"✅ Модель установлена: <b>{model}</b>", parse_mode="HTML")
    await state.clear()


@admin_router.message(Command("cur_model"))
async def show_current_model(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    cur_model = get_current_model()

    await message.answer(f"Сейчас выбрана: \n{cur_model}")


@admin_router.message(Command("logs"))
@admin_router.message(F.text.lower() == "получить логи")
async def send_logs(message: Message):

    await message.bot.send_message(
        chat_id=ADMIN_ID, 
        text=f'Пользователь @{message.from_user.username} \nid: {message.from_user.id} просил логи'
        )
    if message.from_user.id != ADMIN_ID:
        return

    excel_path = os.path.join("logs", "logs.xlsx")

    if os.path.exists(excel_path):
        await message.answer_document(FSInputFile(excel_path))


@admin_router.message(F.text.startswith("Забанить"))
async def handle_block_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, user_str, minutes_str = message.text.split()
        username = user_str.lstrip("@")
        minutes = int(minutes_str)
        block_user(username, minutes)
        await message.answer(f"✅ Пользователь @{username} заблокирован на {minutes} минут.")

    except Exception:
        await message.answer("⚠️ Использование: блок @username 60")


@admin_router.message(F.text.startswith("Разбанить"))
async def handle_unblock_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, user_str = message.text.split()
        username = user_str.lstrip("@")
        unblock_user(username)
        await message.answer(f"🔓 Пользователь @{username} разблокирован.")
    except Exception:
        await message.answer("⚠️ Использование: разблок @username")
