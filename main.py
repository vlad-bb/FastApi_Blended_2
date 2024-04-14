import uvicorn
import json

from fastapi import FastAPI, Request, Query
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router
from fastapi_oauth2.exceptions import OAuth2Error

from src.contacts.routes import router as contacts_router
from src.auth.routes import router as auth_router
from src.payments.services import set_webhook
from src.web_shop.routes import router as web_shop_router
from src.payments.routes import router as payment_router
from src.handlers.oauth_handler import on_auth, get_user_from_token
from src.web_shop.service import bot, dp, WEB_APP_URL, types

from config import oauth2_config
from starlette.config import Config

env_config = Config(".env")

WEBHOOK_PATH = f'/bot/{env_config("TG_TOKEN")}'
WEBHOOK_URL = f"{env_config('WEBHOOK_URL')}{WEBHOOK_PATH}"
print(f"WEBHOOK_URL: {WEBHOOK_URL}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url=WEBHOOK_URL)
    await set_webhook()

    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(contacts_router, prefix='/api')
app.include_router(oauth2_router)
app.include_router(web_shop_router)
app.include_router(payment_router)

app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="src/templates")
app.mount("/static", StaticFiles(directory="src/static"), name="static")


# https://fastapi.tiangolo.com/tutorial/handling-errors/
@app.exception_handler(OAuth2Error)
async def error_handler(request: Request, e: OAuth2Error):
    print("An error occurred in OAuth2Middleware", e)
    return RedirectResponse(url="/", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, token: str = Query(None)):
    # print(f"{request=}, {request.user=}")
    # print(f'{token=}')
    username = None
    avatar = None
    if token:
        user = await get_user_from_token(token)
        username = user.username
        avatar = user.avatar
        request['user']['is_authenticated'] = True
    return templates.TemplateResponse("index.html", {
        "json": json,
        "request": request,
        "username": username,
        "avatar": avatar
    })


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    print(f"Bot receive data from Telegram Server")
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
