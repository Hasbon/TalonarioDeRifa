import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Force SQLite for tests before app imports
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-32chars"
os.environ["CORS_ORIGINS"] = "http://test"

from app.core.enums import UserRole
from app.db.base import Base
from app.db.seed import ensure_raffle_and_tickets
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.security.passwords import hash_password


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db(db_engine):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSession()
    ensure_raffle_and_tickets(session)
    admin = User(
        username="admin",
        password_hash=hash_password("AdminPass123!"),
        full_name="Administrador",
        role=UserRole.ADMIN,
        is_active=True,
    )
    seller = User(
        username="vendedor1",
        password_hash=hash_password("SellerPass123!"),
        full_name="Vendedor Uno",
        role=UserRole.SELLER,
        is_active=True,
    )
    session.add_all([admin, seller])
    session.commit()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_engine, db):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_token(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "AdminPass123!"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def seller_token(client):
    r = client.post("/api/auth/login", json={"username": "vendedor1", "password": "SellerPass123!"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
