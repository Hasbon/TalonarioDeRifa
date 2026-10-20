from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserOut
from app.security.deps import get_current_user
from app.security.jwt import create_access_token
from app.security.passwords import verify_password

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.LOGIN_RATE_LIMIT)
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo")
    token = create_access_token(user.id, extra={"role": user.role.value})
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    # JWT stateless: client discards token. Endpoint kept for API contract.
    return {"detail": "Sesión cerrada", "user_id": user.id}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
