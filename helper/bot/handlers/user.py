from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import Command

from helper.core.qdrant_client import get_qdrant_client
from helper.core.ask_llm import get_answer
from helper.core.model_state import get_current_model
from helper.bot.moderation import is_user_blocked, is_rate_limited
from log_tools.log_worker import log_queue
from config import QDRANT_URL, QDRANT_API_KEY, GROUP_ID, ADMIN_ID


user_router = Router()
qdrant_client = get_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

start_help_message = '''
    👋 Привет! Я — <b>Сигма ПБ Бот</b>, помощник по программе Сигма ПБ. Напишите мне вопрос — я найду ответ в руководстве пользователя.

    ❗ <b>Формулируйте вопрос полностью и точно</b>
    🔴 «Почему не работает программа?»
    🟢 «Почему запущенный расчет ОФП может прерываться без ошибки? Как это исправить?»

    💬 <b>Если вы хотите уточнить что-то, делайте это в одном сообщении:</b>
    ✖️ «Как это исправить?» — <i>не подойдет</i>
    ✔️ «Почему расчет ОФП может прерываться без ошибки? Как это исправить?» — <i>отлично</i>

    📈 <b>Ваши вопросы помогают сделать бота лучше</b>
    Мы видим все вопросы и ответы, чтобы со временем пополнить базу знаний.
'''


@user_router.message(Command("start"))
async def handle_start(message: Message):
    await message.answer(start_help_message, parse_mode='HTML')


@user_router.message(Command("help"))
async def handle_start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "Чтобы забанить напиши:\n"
            "Забанить user_id *кол-во минут*\n\n"
            "Чтобы разбанить напиши:\n"
            "Разбанить user_id \n\n"
            "Чтобы получить логи:\n"
            "Получить логи или /logs\n\n"
            "Сменить модель - /set_model \n"
            "Посмотреть модель - /cur_model \n"
        )
    else:
        await message.answer(start_help_message, parse_mode='HTML')


@user_router.message(F.text)
async def handle_message(message: Message):
    user_message = message.text
    username = message.from_user.username
    user_id = message.from_user.id

    if is_user_blocked(user_id):
        await message.answer("Повторите попытку через несколько минут или обратитесь в техподдержку")
        return

    if is_rate_limited(user_id):
        await message.answer("⏳ Пожалуйста, подождите 20 секунд перед следующим сообщением.")
        return

    status_msg = await message.answer("Обрабатываю ваш вопрос...")

    try:
        current_model = get_current_model()

        got_ans, chapter_ids, chapter_scores, prompt_tokens, response_tokens, used_model = await get_answer(
            user_question=user_message,
            qdrant_client=qdrant_client,
            collection_name="sigmaRP_large",
            model=current_model,
            top_k=3
            )

    except Exception as e:
        await status_msg.delete()
        await message.answer("Произошла ошибка, она уже отправлена службе поддержки. \n"
                             "Если вопрос срочный - напишите на support@3ksigma.ru")
        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ Ошибка у @{username} id={user_id}:\n<pre>{e}</pre>",
            parse_mode="HTML"
        )
        return

    await status_msg.delete()
    await message.answer(got_ans)

    group_text = (
        f'@{username} id={user_id}:\n"{user_message}"\n\n'
        f"<b>{used_model}</b>:\n\"{got_ans}\""
    )
    await message.bot.send_message(chat_id=GROUP_ID, text=group_text, parse_mode='HTML')

    await log_queue.put({
        "username": username,
        "user_id": message.from_user.id,
        "question": user_message,
        "answer": got_ans,
        "input_tokens": prompt_tokens,
        "output_tokens": response_tokens,
        "chapter_ids": chapter_ids,
        "chapter_scores": chapter_scores,
        "model": used_model
    })


@user_router.my_chat_member()
async def on_bot_added_or_changed(event: ChatMemberUpdated, bot):
    chat = event.chat
    if chat.id != GROUP_ID:
        await bot.leave_chat(chat.id)
