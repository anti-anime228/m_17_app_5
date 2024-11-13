from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..backend.db_depends import get_db
from typing import Annotated

from ..models import User
from ..models import Task
from ..schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete

from slugify import slugify

router_user = APIRouter(prefix='/user', tags=['user'])


@router_user.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router_user.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found')
    return user


@router_user.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))
    db.commit()

    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router_user.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, update_user: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found')
    db.execute(update(User).where(User.id == user_id).values(firstname=update_user.firstname,
                                                             lastname=update_user.lastname,
                                                             age=update_user.age,
                                                             ))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router_user.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found')
    db.execute(delete(User).where(User.id == user_id))
    db.execute(delete(Task).where(Task.user_id == user_id))

    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router_user.get('/user_id/tasks')
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user_tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    if user_tasks is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found')
    return user_tasks
