import asyncio

from httpx import ASGITransport, AsyncClient

from auth.jwt_handler import create_access_token, verify_access_token
from auth.m2m import LAB_SCOPE
from main import app

def test_laboratorio_obtem_token_e_consulta_disponibilidade() -> None:
    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token_response = await client.post(
                "/oauth/token",
                auth=("laboratorio-teste", "segredo-laboratorio-teste"),
                data={
                    "grant_type": "client_credentials",
                    "scope": LAB_SCOPE,
                },
            )
            token = token_response.json()["access_token"]
            availability_response = await client.get(
                "/oauth/lab/availability",
                params={"day": "2026-10-10"},
                headers={"Authorization": f"Bearer {token}"},
            )
            return token_response, token, availability_response

    token_response, token, availability_response = asyncio.run(execute())
    claims = verify_access_token(token)

    assert token_response.status_code == 200
    assert token_response.json()["scope"] == LAB_SCOPE
    assert claims["actor_type"] == "laboratory"
    assert claims["sub"] == "laboratorio-teste"
    assert claims["scope"] == LAB_SCOPE
    assert availability_response.status_code == 200
    assert len(availability_response.json()["available_slots"]) == 10

def test_token_laboratorio_nao_acessa_rota_de_usuario() -> None:
    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            token_response = await client.post(
                "/oauth/token",
                auth=("laboratorio-teste", "segredo-laboratorio-teste"),
                data={"grant_type": "client_credentials"},
            )
            token = token_response.json()["access_token"]
            return await client.get(
                "/appointment/",
                headers={"Authorization": f"Bearer {token}"},
            )

    response = asyncio.run(execute())
    assert response.status_code == 403
    assert response.json()["detail"] == "Token de usuário obrigatório"

def test_token_humano_nao_acessa_rota_do_laboratorio() -> None:
    token = create_access_token(
        "profissional@clinica.com",
        actor_type="user",
        role="profissional",
        scopes=[LAB_SCOPE],
    )

    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://app",
        ) as client:
            return await client.get(
                "/oauth/lab/availability",
                params={"day": "2026-10-10"},
                headers={"Authorization": f"Bearer {token}"},
            )

    response = asyncio.run(execute())
    assert response.status_code == 401
    assert response.json()["detail"] == "Token de laboratório inválido"
