import json

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from connect import get_async_session
from src.auth import users as users_repository
from src.auth.schemas import UserSchema, UserResponseSchema, TokenSchema
from src.auth.service import (get_password_hash, verify_password, create_access_token, create_refresh_token,
                              decode_refresh_token)

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()
templates = Jinja2Templates(directory="src/templates")


@router.post('/signup', response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_async_session)):
    exist_user = await users_repository.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')
    body.password = get_password_hash(body.password)
    new_user = await users_repository.create_user(body, db)
    return new_user


@router.post('/login', response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_session)):
    user = await users_repository.get_user_by_email(body.username, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email')
    if not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')
    access_token = await create_access_token(data={'sub': user.email, 'randon phrase': 'kurlic'})  # можу додати будь що
    refresh_token = await create_refresh_token(data={'sub': user.email})
    await users_repository.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: AsyncSession = Depends(get_async_session)):
    token = credentials.credentials

    email = await decode_refresh_token(token)
    user = await users_repository.get_user_by_email(email, db)
    if user.refresh_token != token:
        await users_repository.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

    access_token = await create_access_token(data={'sub': email})
    refresh_token = await create_refresh_token(data={'sub': email})
    await users_repository.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get("/signup_page", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {
        "json": json,
        "request": request,
    })


@router.get("/login_page", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "json": json,
        "request": request,
    })


@router.get("/save_password", response_class=HTMLResponse)
async def save_password(request: Request):
    return templates.TemplateResponse("save_password.html", {
        "json": json,
        "request": request,
    })
