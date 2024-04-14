import os
import json
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import dotenv_values

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram import types, filters
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from starlette.config import Config

config = Config(".env")
WEB_APP_URL = config('WEBAPP_URL')
bot = Bot(token=config("TG_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.USER_IN_CHAT)

router = Router()
dp.include_router(router)

mock_db_path = "mock_db_invoices.json"


@router.message(CommandStart())
async def start_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    print(f'User started the bot. User ID: {user_id}, Chat ID: {chat_id}, First_name: {user_name}')
    button1 = types.KeyboardButton(
        text='Fill the Form', web_app=types.WebAppInfo(url=f'{WEB_APP_URL}/form?userId={user_id}'))
    button2 = types.KeyboardButton(
        text='Create Order')  # , web_app=types.WebAppInfo(url=f'{WEB_APP_URL}?userId={user_id}'))  # через додаткову кнопку
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button1, button2]])
    await message.answer(
        'Welcome to the bot!\nPlease Fill the Form to get 10% discount on your first order.',
        reply_markup=keyboard)


@router.message(F.text.startswith('Create Order'))
async def send_order_creation_message(message: types.Message):
    user_id = message.from_user.id
    inline_button = InlineKeyboardButton(text='Create Order',
                                         web_app=types.WebAppInfo(url=f'{WEB_APP_URL}?userId={user_id}'))
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])
    await message.answer('Go to the web app to create an order.', reply_markup=inline_keyboard)


def save_users_invoice(invoiceId: str, user_id: int):
    """функція імітує збереження інвойсі в БД"""
    if not os.path.exists(mock_db_path):
        with open(mock_db_path, "w") as file:
            json.dump({invoiceId: user_id}, file, indent=4)
    else:
        with open(mock_db_path, "r+") as fh:
            data = json.load(fh)
            data[invoiceId] = user_id
            fh.seek(0)
            json.dump(data, fh, indent=4)


def get_user_id_by_invoice_id(invoiceId: str):
    """функція імітує отримання користувача по інвойсу з БД"""
    if not os.path.exists(mock_db_path):
        return None
    with open(mock_db_path, "r") as fh:
        data = json.load(fh)
        user_id = data.get(invoiceId)
        return user_id
