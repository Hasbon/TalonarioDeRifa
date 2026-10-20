from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.core.enums import CommercialStatus, PaymentStatusSale


class SaleCreate(BaseModel):
    customer_full_name: str = Field(min_length=2, max_length=200)
    customer_phone: str = Field(min_length=7, max_length=32)
    number_code: str
    initial_payment: int = Field(default=0, ge=0)
    payment_method: str | None = Field(default="efectivo", max_length=64)
    payment_reference: str | None = None
    payment_due_date: date | None = None
    internal_notes: str | None = None

    @field_validator("number_code")
    @classmethod
    def validate_number(cls, v: str) -> str:
        if len(v) != 2 or not v.isdigit():
            raise ValueError("El número debe ser una cadena de dos dígitos (00-99)")
        n = int(v)
        if n < 0 or n > 99:
            raise ValueError("El número debe estar entre 00 y 99")
        return f"{n:02d}"


class SaleCancel(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)


class SaleUpdate(BaseModel):
    payment_due_date: date | None = None
    internal_notes: str | None = None


class CustomerOut(BaseModel):
    id: str
    full_name: str
    phone: str

    model_config = {"from_attributes": True}


class SellerBrief(BaseModel):
    id: str
    username: str
    full_name: str

    model_config = {"from_attributes": True}


class PaymentOut(BaseModel):
    id: str
    sale_id: str
    amount: int
    payment_method: str
    payment_reference: str | None
    status: str
    registered_by: str
    payment_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleOut(BaseModel):
    id: str
    ticket_id: str
    number_code: str
    customer: CustomerOut
    seller: SellerBrief
    ticket_price: int
    commercial_status: CommercialStatus
    payment_status: PaymentStatusSale
    total_paid: int
    balance_due: int
    payment_due_date: date | None
    internal_notes: str | None
    assigned_at: datetime
    cancelled_at: datetime | None
    cancellation_reason: str | None
    public_token: str | None = None
    payments: list[PaymentOut] = []

    model_config = {"from_attributes": True}


class PaymentCreate(BaseModel):
    amount: int = Field(gt=0)
    payment_method: str = Field(min_length=2, max_length=64)
    payment_reference: str | None = None
    confirm: bool = True
    notes: str | None = None
