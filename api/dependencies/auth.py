from typing import List, Annotated, Callable

from fastapi import Request, Depends
from sqlalchemy.orm import Session

from core.security import SecurityInstance
from core.db import get_db
from database.repositories import UserRepo
from exceptions import UnAuthorized

def auth_user(request: Request, db: Session = Depends(get_db)):

    payload = SecurityInstance.token_validation(request)

    user_id = payload["sub"]
    user = UserRepo(db).get_by_id(user_id)

    if user is None:
        raise UnAuthorized("User not found",404)

    return user