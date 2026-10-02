import asyncio

from httpx import ASGITransport, AsyncClient

from main import app

def test_cors_permite_somente_origem_configurada() -> None:
    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://app"
        ) as client:
            allowed = await client.options(
                "/user/signin",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                },
            )
            denied = await client.options(
                "/user/signin",
                headers={
                    "Origin": "https://origem-maliciosa.example",
                    "Access-Control-Request-Method": "POST",
                },
            )
            return allowed, denied

    allowed, denied = asyncio.run(execute())
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-origin" not in denied.headers

def test_respostas_possuem_cabecalhos_de_seguranca() -> None:
    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://app"
        ) as client:
            return await client.get("/")

    response = asyncio.run(execute())
    assert response.headers["strict-transport-security"] == (
        "max-age=31536000; includeSubDomains"
    )
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"

def test_login_aplica_rate_limit_diferenciado() -> None:
    async def execute():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://app"
        ) as client:
            responses = []
            for _ in range(6):
                responses.append(
                    await client.post(
                        "/user/signin",
                        data={"username": "inexistente@teste.com", "password": "errada"},
                    )
                )
            return responses

    responses = asyncio.run(execute())
    assert [response.status_code for response in responses[:5]] == [401] * 5
    assert responses[5].status_code == 429
    assert responses[5].headers["retry-after"] == "60"

