import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import TOKEN
from face_generate import generate_faces

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_state = {}


@dp.message(Command("start"))
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="👨 Мужские", callback_data="gender_male")
    kb.button(text="👩 Женские", callback_data="gender_female")
    kb.button(text="🎲 Случайно", callback_data="gender_random")
    kb.adjust(1)

    await message.answer("👋 Выбери пол:", reply_markup=kb.as_markup())


@dp.callback_query(F.data.startswith("gender_"))
async def choose_gender(call: CallbackQuery):
    gender = call.data.split("_")[1]
    user_state[call.from_user.id] = {"gender": gender}

    kb = InlineKeyboardBuilder()
    for n in [1, 3, 5, 10]:
        kb.button(text=str(n), callback_data=f"count_{n}")
    kb.adjust(2)

    await call.message.edit_text("🔢 Сколько лиц?", reply_markup=kb.as_markup())
    await call.answer()


@dp.callback_query(F.data.startswith("count_"))
async def generate(call: CallbackQuery):
    count = int(call.data.split("_")[1])
    gender = user_state.get(call.from_user.id, {}).get("gender", "random")

    await call.message.edit_text(f"⏳ Генерирую {count} лиц...")

    images = generate_faces(count, gender)

    if not images:
        await call.message.answer("❌ Ничего не получилось")
        return

    for img_bytes in images:
        await call.message.answer_photo(BufferedInputFile(img_bytes, "face.jpg"))

    # Финальные кнопки
    kb = InlineKeyboardBuilder()
    kb.button(text="🔁 Ещё", callback_data=f"count_{count}")
    kb.button(text="🏠 В начало", callback_data="restart")
    kb.adjust(1)

    await call.message.answer("✅ Готово!", reply_markup=kb.as_markup())


@dp.callback_query(F.data == "restart")
async def restart(call: CallbackQuery):
    await start(call.message)
    await call.answer()


async def main():
    print("✅ Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())