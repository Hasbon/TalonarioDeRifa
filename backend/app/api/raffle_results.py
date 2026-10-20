from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.lottery import LotteryResultCreate, LotteryResultOut
from app.security.deps import require_admin, require_seller_or_admin
from app.services import lottery as lottery_service

router = APIRouter()


@router.get("/raffle/results", response_model=list[LotteryResultOut])
def list_results(db: Session = Depends(get_db), user: User = Depends(require_seller_or_admin)):
    return lottery_service.list_results(db)


@router.post("/admin/raffle/results", response_model=LotteryResultOut, status_code=201)
def create_result(
    body: LotteryResultCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return lottery_service.create_result(db, body, user)


@router.post("/admin/raffle/results/{result_id}/confirm", response_model=LotteryResultOut)
def confirm_result(
    result_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return lottery_service.confirm_result(db, result_id, user)
