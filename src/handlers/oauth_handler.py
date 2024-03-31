from fastapi_oauth2.middleware import Auth
from fastapi_oauth2.middleware import User
from fastapi import Security
from connect import get_async_session
from src.auth.service import jwt, SECRET_KEY, ALGORITHM, get_password_hash
from src.auth.users import get_user_by_email, create_user


async def on_auth(auth: Auth, user: User):
    # perform a check for user existence in
    # the database and create if not exists
    print(f"{auth=}, {user=}")
    async for db in get_async_session():
        current_user = await get_user_by_email(user.email, db=db)
        if not current_user:
            password = get_password_hash(user.identity)
            avatar = user.avatar_url if user.avatar_url else user.picture
            body = {"username": user.name, "email": user.email, "password": password}
            await create_user(body=body, db=db, avatar=avatar)


async def get_user_from_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload['scope'] == 'access_token':
        email = payload['sub']
        async for db in get_async_session():
            user = await get_user_by_email(email, db=db)
            # print(f"{user.username=}")
            return user
