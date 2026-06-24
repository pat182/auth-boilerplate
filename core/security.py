import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

from core.config import settings
from exceptions import UnAuthorized
from jwt import ExpiredSignatureError, InvalidTokenError


class Security:
    def __init__(
        self,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = settings.JWT_HASHING_ALGORITHM,
        jwt_min: int = settings.JWT_MINUTES,
        jwt_refresh_days: int = settings.JWT_REFRESH_DAYS
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.jwt_min = jwt_min
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
        self.jwt_refresh_days = jwt_refresh_days

    @staticmethod
    def hash_password(password: str) -> str:
        # bcrypt only supports up to 72 bytes
        safe_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(safe_bytes, salt).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        safe_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(safe_bytes, hashed_password.encode("utf-8"))

    def create_token(self, data: dict, expires_delta: Optional[timedelta]) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str):
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except ExpiredSignatureError:
            raise UnAuthorized("Token expired")
        except InvalidTokenError:
            raise UnAuthorized("Invalid token")

    def token_validation(self,request: Request,token_type : str = 'access') -> dict:
        cookie_token = request.cookies.get("access_token") if token_type == 'access' else request.cookies.get("refresh_token")
        header_token = request.headers.get('Authorization')
        if cookie_token and header_token:
            raise UnAuthorized("Both cookie and header present")
        #web

        if cookie_token:
            if request.method != "GET":
                self.verify_csrf(request.headers.get("X-CSRF-Token") if request.headers.get("X-CSRF-Token") else None, request.cookies.get("csrf_token"))
            token = cookie_token
            payload = self.decode_token(token)
            if payload.get('client_type') != "browser":
                raise UnAuthorized("Client Mismatched")
        # app
        elif header_token:
            if not header_token.lower().startswith("bearer "):
                raise UnAuthorized("Missing bearer token")
            if request.headers.get("X-CSRF-Token") or request.cookies.get("csrf_token"):
                raise UnAuthorized("CSRF not allowed in app flow")
            token = header_token.split(" ", 1)[1]
            payload = self.decode_token(token)
            # print(payload)
            if payload.get('client_type') != "app":
                raise UnAuthorized("Token Mismatched")
        else:
            raise UnAuthorized("Token Required")

        if payload.get("type") != token_type:
            raise UnAuthorized("Token Type Mismatched")
        return payload

    @staticmethod
    def verify_csrf(csrf_header: str, csrf_cookie: str):
        if not csrf_cookie or csrf_cookie != csrf_header:
            raise UnAuthorized("CSRF validation failed")

SecurityInstance = Security()
