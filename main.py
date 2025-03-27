import logging
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, Text
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold

TOKEN = "7951207021:AAH_1tSgU0xTCDjeKJ5DBD1B1vA3BYrQ44g"
ADMIN_ID = 7538330099

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())


class Form(StatesGroup):
    category = State()
    name = State()
    surname = State()
    age = State()
    location = State()
    contact = State()
    confirm = State()


@dp.message(Command("start"))
async def start(message: types.Message):
    username = message.from_user.first_name
    text = (f"👋 {hbold(username)}! \n\n"
            "🤖 *UstozShogird* botiga xush kelibsiz!\n"
            "Bu bot orqali quyidagilarni qilishingiz mumkin:\n\n"
            "🔹 Sherik kerak\n"
            "🔹 Ish joyi kerak\n"
            "🔹 Hodim kerak\n"
            "🔹 Ustoz kerak\n"
            "🔹 Shogird kerak\n\n"
            "💡 /help buyrug'i bilan to'liq ma'lumot oling!")
    await message.answer(text, reply_markup=ReplyKeyboardRemove())


@dp.message(Command("help"))
async def help_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Sherik kerak"), KeyboardButton(text="Ish joyi kerak")],
            [KeyboardButton(text="Hodim kerak"), KeyboardButton(text="Ustoz kerak"), KeyboardButton(text="Shogird kerak")]
        ],
        resize_keyboard=True
    )
    await message.answer("🆘 *Yordam Menyusi*\n\nQuyidagi variantlardan birini tanlang:", reply_markup=keyboard)


@dp.message(Text(["Sherik kerak", "Ish joyi kerak", "Hodim kerak", "Ustoz kerak", "Shogird kerak"]))
async def start_conversation(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("✍️ *Ismingizni kiriting:*")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📝 *Familiyangizni kiriting:*")
    await state.set_state(Form.surname)


@dp.message(Form.surname)
async def get_surname(message: types.Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer("🎂 *Yoshingizni kiriting:*")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def get_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 18:
            await message.answer("⚠️ *Iltimos, 18 yosh va undan kattalar uchun!*")
            return
        await state.update_data(age=age)
        await message.answer("🌍 *Lokatsiyangizni yozing:*")
        await state.set_state(Form.location)
    except ValueError:
        await message.answer("❌ *Iltimos, yoshni raqam shaklida kiriting!*")


@dp.message(Form.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer("📞 *Telefon raqamingizni yuboring:*", reply_markup=keyboard)
    await state.set_state(Form.contact)


@dp.message(Form.contact, Text(startswith='+'))
@dp.message(Form.contact, lambda msg: msg.contact)
async def get_contact(message: types.Message, state: FSMContext):
    contact = message.contact.phone_number if message.contact else message.text
    await state.update_data(contact=contact)
    data = await state.get_data()
    user_info = (f"📌 *E'lon turi:* {data['category']}\n"
                 f"👤 *Ism:* {data['name']}\n"
                 f"👤 *Familiya:* {data['surname']}\n"
                 f"🎂 *Yosh:* {data['age']}\n"
                 f"📍 *Lokatsiya:* {data['location']}\n"
                 f"📞 *Kontakt:* {data['contact']}\n\n"
                 "✅ *Ma'lumotlar to'g'rimi?*")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo'q")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(user_info, reply_markup=keyboard)
    await state.set_state(Form.confirm)


@dp.message(Form.confirm, Text("✅ Ha"))
async def confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_info = (f"📌 *Yangi e'lon:* {data['category']}\n"
                 f"👤 *Ism:* {data['name']}\n"
                 f"👤 *Familiya:* {data['surname']}\n"
                 f"🎂 *Yosh:* {data['age']}\n"
                 f"📍 *Lokatsiya:* {data['location']}\n"
                 f"📞 *Kontakt:* {data['contact']}")
    await bot.send_message(ADMIN_ID, user_info)
    await message.answer("✅ *Ma'lumotlaringiz yuborildi!*", reply_markup=ReplyKeyboardRemove())
    await state.clear()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())