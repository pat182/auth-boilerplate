from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter,Request,Depends,Response,Cookie
from sqlalchemy.orm import Session

from api.return_schemas import LoginRequest,TokenResponse,Tokens,AppTokens
from core.config import settings
from core.db import get_db
from api.services.auth_service import AuthService
from helper import set_auth_cookies,clear_auth_cookies
from core.security import SecurityInstance
from database.models import UserRefreshToken
from exceptions import UnAuthorized

router = APIRouter(
    prefix=f"{settings.API_PREFIX}"
)

@router.post("/app/auth",response_model=TokenResponse)
def app_login(request: Request,
    body: LoginRequest,db: Annotated[Session, Depends(get_db)],response: Response):
    auth = AuthService(db, response, request.state.device_info,'app')

    token_data = auth.access_tokens(email=body.email, password=body.password)
    return TokenResponse(
        token=AppTokens(**token_data),
        csrf=None,
        user=token_data['user']
    )

@router.post("/auth",response_model=TokenResponse)
def login(request:Request,body: LoginRequest,db: Annotated[Session, Depends(get_db)], response: Response):
    auth = AuthService(db, response,request.state.device_info)
    token_data = auth.access_tokens(email=body.email, password=body.password)
    set_auth_cookies(
        response, access_token=token_data['access_token'],
        refresh_token=token_data['refresh_token'],
        csrf_token=token_data['csrf_token'],
        access_exp=token_data['expires_in'],
        refresh_exp=token_data['r_expires_in'],
    )
    return TokenResponse(
        token=Tokens(**token_data),
        csrf=token_data['csrf_token'],
        user=token_data['user']
    )

@router.post("/refresh")
def refresh(
    response: Response,
    request : Request,
    db: Session = Depends(get_db),
    refresh_token: str = Cookie(None),
):
    auth = AuthService(db,response,request.state.device_info)
    payload = SecurityInstance.token_validation(request,'refresh')


    if payload.get('client_type') == 'browser':
        token_data = auth.refresh_tokens(refresh_token, payload)
        token_response = Tokens(**token_data)
        set_auth_cookies(
            response,
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            csrf_token= token_data['csrf_token'] if token_data['csrf_token'] else request.headers.get("X-CSRF-Token"),
            access_exp=token_data['expires_in'],
            refresh_exp=token_data['r_expires_in']
        )
    else:
        token_data = auth.refresh_tokens(request.headers.get("Authorization"), payload)
        token_response = AppTokens(**token_data)

    return TokenResponse(
        token=token_response,
        csrf=token_data['csrf_token'],
        user=token_data['user']
    )

@router.post("/logout")
def logout(response: Response,
    request : Request,
    db: Session = Depends(get_db)):

    payload = SecurityInstance.token_validation(request, 'refresh')
    db_token = db.query(UserRefreshToken).filter_by(user_id=payload['sub'], jti=payload['jti'], revoked=False).first()

    if not db_token:
        raise UnAuthorized("Token already revoked")

    if payload.get('client_type') == 'browser':
        clear_auth_cookies(response)

    db_token.revoked = True
    db_token.revoked_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "successfully logged out"}