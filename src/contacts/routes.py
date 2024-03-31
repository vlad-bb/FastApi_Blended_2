from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from connect import get_async_session
from src.contacts.enums import SearchParams
from src.contacts.schemas import ContactSchema, ContactResponseSchema
from src.contacts import repository as contacts_repository

from src.models import User, Role
from src.auth.roles import RoleAccess
from src.auth.service import get_current_user

router = APIRouter(prefix='/contacts', tags=['contacts'])
access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.post('/', response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(get_current_user)):
    return await contacts_repository.create_contact(body, db, user)


@router.get('/', response_model=list[ContactResponseSchema])
async def read_contacts(skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1),
                        db: AsyncSession = Depends(get_async_session),
                        user: User = Depends(get_current_user)):
    return await contacts_repository.get_contacts(skip, limit, db, user)


@router.get('/all/', response_model=list[ContactResponseSchema], dependencies=[Depends(access_to_route_all)])
async def read_contacts(skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1),
                        db: AsyncSession = Depends(get_async_session),
                        user: User = Depends(get_current_user)):
    return await contacts_repository.get_all_contacts(skip, limit, db, user)


@router.get('/search/', response_model=list[ContactResponseSchema])
async def search_contact(param: SearchParams, value: str, db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(get_current_user)):
    contact = await contacts_repository.search_contact(param, value, db, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contact


@router.get('/birthday/', response_model=list[ContactResponseSchema])
async def birthday_contact(db: AsyncSession = Depends(get_async_session),
                           user: User = Depends(get_current_user)):
    contact = await contacts_repository.get_upcoming_birthdays(db, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contact


@router.get('/{contact_id}', response_model=ContactResponseSchema)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_async_session),
                      user: User = Depends(get_current_user)):
    contact = await contacts_repository.get_contact(contact_id, db, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.put('/{contact_id}', response_model=ContactResponseSchema)
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1),
                         db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(get_current_user)):
    contact = await contacts_repository.update_contact(contact_id, body, db, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.delete('/{contact_id}', response_model=ContactResponseSchema)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(get_current_user)):
    contact = await contacts_repository.delete_contact(contact_id, db, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
