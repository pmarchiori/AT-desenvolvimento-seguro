import asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from database.connection import get_session
from main import app


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(test_engine)


async def get_test_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session


def test_criar_consulta_com_sucesso() -> None:
    async def executar_requisicao():
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.post(
                "/consultas/",
                json={
                    "paciente_id": 1,
                    "profissional_id": 2,
                    "data_hora": "2026-10-15T14:30:00",
                    "status": "agendada",
                },
            )

    resposta = asyncio.run(executar_requisicao())

    assert resposta.status_code == 201
    assert resposta.json() == {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-15T14:30:00",
        "status": "agendada",
        "id": 1,
    }
