import uvicorn
import json

from fastapi import FastAPI, Request, Query
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router
from fastapi_oauth2.exceptions import OAuth2Error

from src.contacts.routes import router as contacts_router
from src.auth.routes import router as auth_router
from src.handlers.oauth_handler import on_auth, get_user_from_token
from config import oauth2_config

app = FastAPI()

app.include_router(auth_router)
app.include_router(contacts_router, prefix='/api')
app.include_router(oauth2_router)

app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)

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


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
