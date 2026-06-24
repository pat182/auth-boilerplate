from typing import Optional,Union

from pydantic import BaseModel
from api.return_schemas import UserResponse


class Tokens(BaseModel):
    expires_in: int
    expires_at: str
    r_expires_in: int
    r_expires_at: str

class AppTokens(BaseModel):
    access_token : str
    expires_in: int
    expires_at: str
    refresh_token: str
    r_expires_in: int
    r_expires_at: str

class TokenResponse(BaseModel):
    csrf: Optional[str] = None
    token : Union[Tokens,AppTokens]
    user: UserResponse
