from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api import api_router
from app.api.auth import limiter as auth_limiter
from app.core.config import get_settings
from app.db.base import Base
from app.db.seed import ensure_raffle_and_tickets
from app.db.session import SessionLocal, engine
import app.models  # noqa: F401 — register models


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_raffle_and_tickets(db)
    finally:
        db.close()
    yield


settings = get_settings()
app = FastAPI(
    title="Rifa Digital API",
    description="API para administración de rifa digital con talonario 00-99",
    version="1.0.0",
    lifespan=lifespan,
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = auth_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
