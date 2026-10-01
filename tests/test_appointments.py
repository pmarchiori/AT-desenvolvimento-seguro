import asyncio
from datetime import date, datetime, time

from httpx import ASGITransport, AsyncClient
from sqlmodel import Session

from auth.hash_password import HashPassword
from main import app
from models.appointments import Appointment
from models.patients import Patient
from models.users import User
from tests.conftest import test_engine

hasher = HashPassword()

def seed_database() -> None:
    with Session(test_engine) as session:
        session.add(
            User(
                id=1,
                name="Ana",
                email="ana@clinica.com",
                password=hasher.create_hash("123"),
                role="recepcionista",
            )
        )
        session.add(
            User(
                id=2,
                name="Dr. House",
                email="house@clinica.com",
                password=hasher.create_hash("123"),
                role="profissional",
            )
        )
        session.add(
            Patient(
                id=1,
                name="Paciente Teste",
                cpf="12345678900",
                phone="21999999999",
            )
        )
        session.commit()


async def login(client: AsyncClient, email: str) -> str:
    response = await client.post(
        "/user/signin",
        data={"username": email, "password": "123"},
    )
    return response.json()["access_token"]

def test_recepcionista_pode_criar_consulta_sem_expor_campos_internos() -> None:
    seed_database()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token = await login(client, "ana@clinica.com")
            return await client.post(
                "/appointment/new",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "patient_id": 1,
                    "professional_id": 2,
                    "date_time": "2026-10-10T10:00:00",
                    "notes": "Informação confidencial",
                },
            )

    response = asyncio.run(execute())

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "patient_id": 1,
        "professional_id": 2,
        "date_time": "2026-10-10T10:00:00",
        "status": "agendada",
    }
    assert "notes" not in response.json()
    assert "created_at" not in response.json()

def test_medico_nao_pode_criar_consulta() -> None:
    seed_database()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token = await login(client, "house@clinica.com")
            return await client.post(
                "/appointment/new",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "patient_id": 1,
                    "professional_id": 2,
                    "date_time": "2026-10-10T10:00:00",
                },
            )

    response = asyncio.run(execute())
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]

def test_agenda_escapa_conteudo_html() -> None:
    seed_database()
    with Session(test_engine) as session:
        session.add(
            Appointment(
                patient_id=1,
                professional_id=2,
                date_time=datetime.combine(date.today(), time(hour=9)),
                status="<script>alert('xss')</script>",
            )
        )
        session.commit()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token = await login(client, "ana@clinica.com")
            assert token
            return await client.get("/appointment/agenda")

    response = asyncio.run(execute())
    assert response.status_code == 200
    assert "<script>" not in response.text
    assert "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;" in response.text
