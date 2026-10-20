import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SELLER = "seller"


class RaffleStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    DRAWN = "drawn"


class CommercialStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class PaymentStatusSale(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"


class PaymentRecordStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    VOIDED = "voided"


class VerificationStatus(str, enum.Enum):
    DRAFT = "draft"
    VERIFIED = "verified"
    CONFIRMED = "confirmed"
