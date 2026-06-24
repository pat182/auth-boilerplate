from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.base_exception import AppException
from api.routes import auth_router,convert_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type","X-CSRF-Token","X-Client-Type"],
)

@app.get("/api")
def show():
    return settings.dict()

app.include_router(auth_router)
app.include_router(convert_router)

@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )

@app.middleware("http")
async def check_client_type(request: Request, call_next):
    auth_header = request.headers.get("Authorization", "").lower()

    if auth_header.startswith("bearer "):
        client_type = "app"
    else:
        client_type = "browser"

    request.state.client_type = client_type
    request.state.device_info = request.headers.get("User-Agent",f"Unknown-{client_type}")
    return await call_next(request)
