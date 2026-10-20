"""Create the first administrator securely from the command line.

Usage:
  python -m app.scripts.create_admin --username admin --full-name "Admin" --password "..."
"""

from __future__ import annotations

import argparse
import getpass
import sys

from app.core.enums import UserRole
from app.db.base import Base
from app.db.seed import ensure_raffle_and_tickets
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.security.passwords import hash_password
import app.models  # noqa: F401


def main() -> int:
    parser = argparse.ArgumentParser(description="Crear administrador inicial")
    parser.add_argument("--username", required=True)
    parser.add_argument("--full-name", required=True)
    parser.add_argument("--password", default=None, help="Si se omite, se solicita de forma interactiva")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Contraseña (mín. 10 caracteres): ")
    if len(password) < 10:
        print("Error: la contraseña debe tener al menos 10 caracteres.", file=sys.stderr)
        return 1

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_raffle_and_tickets(db)
        if db.query(User).filter(User.username == args.username).first():
            print(f"Error: el usuario '{args.username}' ya existe.", file=sys.stderr)
            return 1
        user = User(
            username=args.username,
            password_hash=hash_password(password),
            full_name=args.full_name,
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"Administrador '{args.username}' creado correctamente.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
