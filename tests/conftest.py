import os

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

os.environ["SECRET_KEY"] = "chave-exclusiva-do-ambiente-de-testes"
os.environ["MFA_CODE"] = "123456"
os.environ["COOKIE_SECURE"] = "false"
os.environ["LAB_CLIENT_ID"] = "laboratorio-teste"
os.environ["LAB_CLIENT_SECRET"] = "segredo-laboratorio-teste"

from database.connection import get_session
from main import app
from security.http import login_rate_limiter

#importação dos modelos
from models.appointments import Appointment
from models.patients import Patient
from models.users import User

#configurar banco em memória
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

async def override_get_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(autouse=True)
def reset_test_database():
    login_rate_limiter.reset()
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield
