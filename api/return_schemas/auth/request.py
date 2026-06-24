import re
from typing import Optional
from pydantic import BaseModel, field_validator

EMAIL_REGEX = re.compile(r'''
    ^[A-Za-z0-9._%+-]+
    @
    [A-Za-z0-9.-]+
    \.[A-Za-z]{2,}$
    ''', re.VERBOSE)

class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v