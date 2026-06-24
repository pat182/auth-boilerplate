from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    email: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)