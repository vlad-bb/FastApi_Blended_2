from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from src.web_shop.service import bot

from src.payments.schemas import InvoiceRequest
from src.web_shop.service import get_user_id_by_invoice_id

router = APIRouter(tags=["payment"], prefix='/payment')


@router.get("/web-shop", status_code=status.HTTP_200_OK)
async def get_answer_to_mono():
    """Функція відповіді на запит Моно про вебхук"""
    print("Mono ask about webhook")
    return {"ok": True}


@router.post("/web-shop", status_code=status.HTTP_200_OK)
async def invoice_handler(data: InvoiceRequest):
    """Функція обробки інвойсів від Моно"""
    print("Mono invoice_handler started")
    print(f"{data=}")
    print(f"Status: {data.status, type(data.status)}")
    if str(data.status) == "success":
        print('in success')
        invoiceId = data.invoiceId
        user_id = get_user_id_by_invoice_id(invoiceId=invoiceId)
        print(f"{user_id=}")
        info = "Payment for order is success\n" \
               "Wait for delivery number"
        await bot.send_message(chat_id=user_id, text=info)

    return {"ok": True}
