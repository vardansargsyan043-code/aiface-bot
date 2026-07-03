import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import TOKEN
from face_generate import generate_fake_face

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# 🧠 СТАБИЛЬНОСТЬ СИСТЕМЫ
# =========================

queue = asyncio.Queue()
processing = False
processing_users = set()

user_state = {}


# =========================
# 🚀 START
# =========================
@dp.message(Command("start"))
async def start(message):
    kb = InlineKeyboardBuilder()
    kb.button(text="👨 Мужские", callback_data="gender_male")
    kb.button(text="👩 Женские", callback_data="gender_female")
    kb.button(text="🎲 Случайно", callback_data="gender_random")
    kb.adjust(3)

    await message.answer("👋 Выбери пол:", reply_markup=kb.as_markup())


# =========================
# 🎯 ВЫБОР ПОЛА
# =========================
@dp.callback_query(F.data.startswith("gender_"))
async def choose_gender(call: CallbackQuery):
    gender = call.data.split("_")[1]
    user_state[call.from_user.id] = {"gender": gender}

    kb = InlineKeyboardBuilder()
    kb.button(text="5", callback_data="count_5")
    kb.button(text="10", callback_data="count_10")
    kb.button(text="20", callback_data="count_20")
    kb.adjust(3)

    await call.message.answer("🔢 Выбери количество:", reply_markup=kb.as_markup())
    await call.answer()


# =========================
# 📥 ДОБАВЛЕНИЕ В ОЧЕРЕДЬ
# =========================
@dp.callback_query(F.data.startswith("count_"))
async def add_to_queue(call: CallbackQuery):
    user_id = call.from_user.id

    if user_id in processing_users:
        await call.answer("⏳ уже генерируется...", show_alert=True)
        return

    count = int(call.data.split("_")[1])
    gender = user_state.get(user_id, {}).get("gender", "random")

    await queue.put((call, user_id, count, gender))
    await call.answer("📥 добавлено в очередь")

    await process_queue()


# =========================
# ⚙️ ОБРАБОТКА ОЧЕРЕДИ
# =========================
async def process_queue():
    global processing

    if processing:
        return

    processing = True

    while not queue.empty():
        call, user_id, count, gender = await queue.get()

        try:
            processing_users.add(user_id)

            await call.message.answer(f"⏳ генерирую {count} ({gender})...")

            files = generate_fake_face(count=count, gender=gender)

            if not files:
                await call.message.answer("❌ ошибка генерации")
                continue

            user_state[user_id]["last"] = {
                "count": count,
                "gender": gender
            }

            # 📤 отправка фото
            for f in files:
                await call.message.answer_photo(FSInputFile(f))

            # кнопки
            kb = InlineKeyboardBuilder()
            kb.button(text="🔁 Ещё", callback_data="repeat")
            kb.button(text="⚙️ Изменить", callback_data="restart")
            kb.adjust(2)

            await call.message.answer("👇 дальше:", reply_markup=kb.as_markup())

        finally:
            processing_users.discard(user_id)
            queue.task_done()

    processing = False


# =========================
# 🔁 ПОВТОР
# =========================
@dp.callback_query(F.data == "repeat")
async def repeat(call: CallbackQuery):
    user_id = call.from_user.id
    state = user_state.get(user_id)

    if not state or "last" not in state:
        await call.message.answer("❌ нет данных")
        return

    last = state["last"]

    await queue.put((call, user_id, last["count"], last["gender"]))
    await process_queue()

    await call.answer()


# =========================
# 🔄 РЕСТАРТ
# =========================
@dp.callback_query(F.data == "restart")
async def restart(call: CallbackQuery):
    await start(call.message)
    await call.answer()


# =========================
# ▶️ ЗАПУСК
# =========================
async def main():
    print("✅ BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())