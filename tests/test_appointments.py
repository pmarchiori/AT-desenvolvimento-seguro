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
            User(
                id=3,
                name="Administrador",
                email="admin@clinica.com",
                password=hasher.create_hash("123"),
                role="admin",
            )
        )
        session.add(
            User(
                id=4,
                name="Dra. Wilson",
                email="wilson@clinica.com",
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
                professional_id=2,
            )
        )
        session.commit()

async def login(client: AsyncClient, email: str) -> str:
    response = await client.post(
        "/user/signin",
        data={"username": email, "password": "123"},
    )
    return response.json()["access_token"]

def test_profissional_cria_consulta_do_proprio_paciente() -> None:
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

def test_recepcionista_nao_acessa_rota_de_administrador() -> None:
    seed_database()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token = await login(client, "ana@clinica.com")
            return await client.get(
                "/user/admin",
                headers={"Authorization": f"Bearer {token}"},
            )

    response = asyncio.run(execute())
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]

def test_recepcionista_nao_pode_criar_consulta() -> None:
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
                    "date_time": "2026-10-10T10:00:00",
                },
            )

    response = asyncio.run(execute())
    assert response.status_code == 403

def test_profissional_nao_acessa_consulta_de_outro_profissional() -> None:
    seed_database()
    with Session(test_engine) as session:
        session.add(
            Appointment(
                patient_id=1,
                professional_id=4,
                date_time=datetime(2026, 10, 10, 11, 0),
            )
        )
        session.commit()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token = await login(client, "house@clinica.com")
            return await client.get(
                "/appointment/1",
                headers={"Authorization": f"Bearer {token}"},
            )

    response = asyncio.run(execute())
    assert response.status_code == 403
    assert "próprias consultas" in response.json()["detail"]

def test_profissional_nao_altera_consulta_de_outro_profissional() -> None:
    seed_database()
    with Session(test_engine) as session:
        session.add(
            Appointment(
                id=1,
                patient_id=1,
                professional_id=4,
                date_time=datetime(2026, 10, 10, 11, 0),
            )
        )
        session.commit()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token = await login(client, "house@clinica.com")
            return await client.put(
                "/appointment/edit/1",
                headers={"Authorization": f"Bearer {token}"},
                json={"status": "cancelada"},
            )

    response = asyncio.run(execute())
    assert response.status_code == 403

def test_profissional_nao_exclui_consulta_de_outro_profissional() -> None:
    seed_database()
    with Session(test_engine) as session:
        session.add(
            Appointment(
                id=1,
                patient_id=1,
                professional_id=4,
                date_time=datetime(2026, 10, 10, 11, 0),
            )
        )
        session.commit()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token = await login(client, "house@clinica.com")
            return await client.delete(
                "/appointment/delete/1",
                headers={"Authorization": f"Bearer {token}"},
            )

    response = asyncio.run(execute())
    assert response.status_code == 403

def test_admin_conclui_mfa_e_acessa_rota_restrita() -> None:
    seed_database()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            signin = await client.post(
                "/user/signin",
                data={"username": "admin@clinica.com", "password": "123"},
            )
            mfa = await client.post(
                "/user/mfa",
                json={
                    "mfa_token": signin.json()["mfa_token"],
                    "code": "123456",
                },
            )
            assert mfa.status_code == 200, mfa.text
            access_token = mfa.json()["access_token"]
            admin_response = await client.get(
                "/user/admin",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            return signin, mfa, admin_response

    signin, mfa, admin_response = asyncio.run(execute())
    assert signin.status_code == 200
    assert signin.json()["mfa_required"] is True
    assert mfa.status_code == 200
    assert admin_response.status_code == 200

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
