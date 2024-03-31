from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract, and_, or_

from src.models import Contact, User
from src.contacts.schemas import ContactSchema


async def create_contact(body: ContactSchema, db: AsyncSession, user: User) -> Contact:
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contacts(skip: int, limit: int, db: AsyncSession, user: User):
    contacts = await db.execute(select(Contact).filter_by(user=user).offset(skip).limit(limit))
    return contacts.scalars().all()


async def get_all_contacts(skip: int, limit: int, db: AsyncSession, user: User):
    contacts = await db.execute(select(Contact).offset(skip).limit(limit))
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    contact = await db.execute(select(Contact).filter_by(id=contact_id, user=user))
    return contact.scalar_one_or_none()


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User) -> Contact | None:
    contact = await db.execute(select(Contact).filter_by(id=contact_id, user=user))
    contact = contact.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.second_name = body.second_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.address = body.address
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User) -> Contact | None:
    contact = await db.execute(select(Contact).filter_by(id=contact_id, user=user))
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contact(param: str, value: str, db: AsyncSession, user: User):
    filter_criteria = {
        'id': Contact.id,
        'name': Contact.name,
        'second_name': Contact.second_name,
        'email': Contact.email,
        'phone': Contact.phone,
    }
    contact = await db.execute(select(Contact).filter(filter_criteria[param].like(f"%{value}%")).filter_by(user=user))
    return contact.scalars().all()


async def get_upcoming_birthdays(db: AsyncSession, user: User):
    current_date = datetime.now().date()
    next_week = current_date + timedelta(days=7)
    current_month = current_date.month
    next_month = (current_month % 12) + 1
    contacts = await db.execute(select(Contact).filter(
            or_(
                and_(
                    extract('month', Contact.birthday) == current_date.month,
                    extract('day', Contact.birthday).between(current_date.day, 31)
                ),
                and_(
                    extract('month', Contact.birthday) == next_month,
                    extract('day', Contact.birthday).between(1, next_week.day)
                )
            )
        ).filter_by(user=user)
    )
    return contacts.scalars().all()
