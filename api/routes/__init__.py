from .authentication import router as auth_router
from .random_stuff.convert import router as convert_router

__all__ = [
    "auth_router",
    "convert_router",
]