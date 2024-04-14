from fastapi import APIRouter, Depends, HTTPException, status, Path, Query

from src.payments.services import create_invoice
from src.web_shop.service import bot, InlineKeyboardButton, InlineKeyboardMarkup, types, WEB_APP_URL, save_users_invoice

from src.web_shop.schemas import WebShopRequest

router = APIRouter(tags=["web-shop"])


@router.post("/web-data")
async def handle_web_data(data: WebShopRequest):
    print("Start func handle_web_data")
    print('Data:', data)
    user_id = data.user.get('id')
    info = f"Thank you for your order {data.user.get('first_name')}\nCart items:\n"
    for item in data.products:
        info += f"{item.get('title')} {item.get('description')} {item.get('price')} $\n"
    info += f'Total price: {data.totalPrice} $'
    payment_data = create_invoice(total_price=data.totalPrice, products=data.products)
    invoiceId = payment_data.get('invoiceId')
    save_users_invoice(invoiceId=invoiceId, user_id=user_id)
    pageUrl = payment_data.get('pageUrl')
    inline_button = InlineKeyboardButton(text='Pay by monopay', url=pageUrl)
                                         # web_app=types.WebAppInfo(url=pageUrl))  # todo find solution for pay by QR in telegram brouser
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])
    await bot.send_message(chat_id=user_id, text=info, reply_markup=inline_keyboard)
