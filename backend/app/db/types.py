from enum import Enum as PyEnum
from typing import Type

from sqlalchemy import Enum


def str_enum(enum_cls: Type[PyEnum], **kwargs):
    """SQLAlchemy Enum that persists Python enum *values* (e.g. active), not names (ACTIVE)."""
    return Enum(
        enum_cls,
        values_callable=lambda members: [item.value for item in members],
        **kwargs,
    )
