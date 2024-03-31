from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.models import User
from src.auth.schemas import UserSchema


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    user = await db.execute(select(User).filter_by(email=email))
    return user.scalar_one_or_none()


async def create_user(body: UserSchema | dict, db: AsyncSession, avatar=None) -> User:
    if not avatar:
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as err:
            print(err)
    if isinstance(body, UserSchema):
        new_user = User(**body.model_dump(), avatar=avatar)
    else:
        new_user = User(**body, avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()
