from fastapi import APIRouter
from core.config import settings

router = APIRouter(
    prefix=f"{settings.API_PREFIX}"
)

@router.get("/convert")
def convert():
    return {"message":"Hello World"}