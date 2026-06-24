import secrets, uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from fastapi import Response

from core.security import SecurityInstance
from database.models import User,UserRefreshToken
from exceptions import UnAuthorized
from helper import clear_auth_cookies

class AuthService:
    def __init__(self, db: Session, response: Response,device_info: str ,client_type: str = 'browser'):
        self.db = db
        self.response = response
        self.client_type = client_type
        self.device_info = device_info

    def access_tokens(self, email: str, password: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()

        csrf_token = secrets.token_urlsafe(32)
        if not user or not SecurityInstance.verify_password(password, user.hashed_password):
            raise UnAuthorized("Invalid credentials")

        access_token_expires = timedelta(minutes=SecurityInstance.jwt_min)
        access_token = SecurityInstance.create_token(
            data={
                "sub": str(user.id),
                # "role_id": user.role_id,
                "client_type": self.client_type,
                "type": "access"
            },
            expires_delta=access_token_expires
        )
        expires_at = datetime.now(timezone.utc) + access_token_expires

        refresh_token_expires = timedelta(days=SecurityInstance.jwt_refresh_days)
        jti = str(uuid.uuid4())
        refresh_token = SecurityInstance.create_token(
            data={
                "sub": str(user.id),
                # "remember_me": remember_me,
                "type": "refresh",
                "client_type": self.client_type,
                "jti": jti,  # <-- added unique ID
                "iat": datetime.now(timezone.utc).timestamp()  # <-- added issued-at
            },
            expires_delta=refresh_token_expires
        )
        r_expires_at = datetime.now(timezone.utc) + refresh_token_expires
        db_ref_token = UserRefreshToken(
            user_id = user.id,
            jti = jti,
            refresh_token = refresh_token,
            device_info = self.device_info,
            expires_at=r_expires_at,
            revoked=False
        )
        self.db.add(db_ref_token)
        self.db.commit()
        return {
            "access_token": access_token,
            "expires_in": int(access_token_expires.total_seconds()),
            "expires_at": f"{expires_at} UTC", "refresh_token": refresh_token,
            "r_expires_in": int(refresh_token_expires.total_seconds()),
            "r_expires_at": f"{r_expires_at} UTC",
            "csrf_token": csrf_token,
            "user": user
        }

    def refresh_tokens(self, refresh_token: str,payload : dict) -> dict:
        if not refresh_token:
            raise UnAuthorized("Missing refresh token")

        if payload.get("type") != "refresh":
            clear_auth_cookies(self.response)
            raise UnAuthorized("Invalid token type")

        db_token = self.db.query(UserRefreshToken).filter_by(user_id=int(payload["sub"]), jti=payload["jti"], revoked=False).first()

        if not db_token or db_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
            clear_auth_cookies(self.response)
            raise UnAuthorized("Refresh token expired or revoked")

        user = self.db.query(User).filter(User.id == int(payload.get("sub"))).first()
        if not user:
            clear_auth_cookies(self.response)
            raise UnAuthorized(status_code=404, msg="User not found")

        csrf_token = None if payload['client_type'] == 'app' else secrets.token_urlsafe(32)

        access_token_expires = timedelta(minutes=SecurityInstance.jwt_min)
        access_token = SecurityInstance.create_token(
            data={
                "sub": str(user.id),
                # "role_id": user.role_id,
                "client_type": payload.get("client_type"),
                "type": "access"
            },
            expires_delta=access_token_expires
        )
        expires_at = datetime.now(timezone.utc) + access_token_expires
        refresh_token_expires = timedelta(days=SecurityInstance.jwt_refresh_days)
        new_jti = str(uuid.uuid4())
        new_refresh_token = SecurityInstance.create_token(
                data={
                    "sub": str(user.id),
                    "remember_me": True,
                    "type": "refresh",
                    "client_type": payload.get("client_type"),
                    "jti": new_jti,
                    "iat": datetime.now(timezone.utc).timestamp()
                },
                expires_delta=refresh_token_expires
        )
        refresh_expires_at = datetime.now(timezone.utc) + refresh_token_expires
        db_token.jti = new_jti
        db_token.refresh_token = new_refresh_token
        db_token.expires_at = refresh_expires_at
        self.db.commit()
        return {
            "csrf_token": csrf_token,
            'access_token' : access_token,
            "expires_in": int(access_token_expires.total_seconds()),
            "expires_at": f"{expires_at} UTC",
            'refresh_token': new_refresh_token,
            "r_expires_in": int((refresh_expires_at - datetime.now(timezone.utc)).total_seconds()),
            "r_expires_at": f"{refresh_expires_at} UTC",
            "user": user
        }