import asyncio
from datetime import datetime

from httpx import ASGITransport, AsyncClient
from sqlmodel import Session

from main import app
from models.appointments import Appointment
from tests.conftest import test_engine
from tests.test_appointments import login, seed_database

def test_rejeita_campo_extra_em_consulta() -> None:
    seed_database()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://app"
        ) as client:
            token = await login(client, "house@clinica.com")
            return await client.post(
                "/appointment/new",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "patient_id": 1,
                    "professional_id": 4,
                    "date_time": "2026-10-10T10:00:00",
                },
            )

    response = asyncio.run(execute())
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.extra"

def test_rejeita_xss_em_status_por_whitelist() -> None:
    seed_database()
    with Session(test_engine) as session:
        session.add(
            Appointment(
                id=1,
                patient_id=1,
                professional_id=2,
                date_time=datetime(2026, 10, 10, 10, 0),
            )
        )
        session.commit()

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://app"
        ) as client:
            token = await login(client, "house@clinica.com")
            return await client.put(
                "/appointment/edit/1",
                headers={"Authorization": f"Bearer {token}"},
                json={"status": "<script>alert('xss')</script>"},
            )

    response = asyncio.run(execute())
    assert response.status_code == 422

def test_rejeita_formato_invalido_e_id_controlado_em_paciente() -> None:
    seed_database()

    async def execute(payload):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://app"
        ) as client:
            token = await login(client, "ana@clinica.com")
            return await client.post(
                "/patient/new",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )

    injection = asyncio.run(
        execute(
            {
                "name": "Paciente Teste",
                "cpf": "12345678900' OR '1'='1",
                "phone": "21999999999",
                "professional_id": 2,
            }
        )
    )
    extra_id = asyncio.run(
        execute(
            {
                "id": 99,
                "name": "Outro Paciente",
                "cpf": "98765432100",
                "phone": "21988888888",
                "professional_id": 2,
            }
        )
    )

    assert injection.status_code == 422
    assert extra_id.status_code == 422

def test_endpoint_adicional_signup_rejeita_role() -> None:
    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://app"
        ) as client:
            return await client.post(
                "/user/signup",
                json={
                    "name": "Usuario Teste",
                    "email": "usuario@teste.com",
                    "password": "senha-segura",
                    "role": "admin",
                },
            )

    response = asyncio.run(execute())
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.extra"

def test_middleware_rejeita_jwt_invalido() -> None:
    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://app"
        ) as client:
            return await client.get(
                "/appointment/",
                headers={"Authorization": "Bearer token-adulterado"},
            )

    response = asyncio.run(execute())
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido ou expirado"

