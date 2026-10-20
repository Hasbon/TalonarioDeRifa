from fastapi import APIRouter

from app.api import admin, auth, payments, public, raffle_results, sales

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(raffle_results.router, tags=["results"])
