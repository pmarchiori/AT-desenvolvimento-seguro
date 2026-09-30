from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from database.connection import get_session
from models.consultas import Consulta, ConsultaCreate, ConsultaUpdate


consulta_router = APIRouter(tags=["Consultas"])


@consulta_router.get("/", response_model=list[Consulta])
async def listar_consultas(session: Session = Depends(get_session)) -> list[Consulta]:
    return list(session.exec(select(Consulta)).all())


@consulta_router.get("/{consulta_id}", response_model=Consulta)
async def buscar_consulta(
    consulta_id: int,
    session: Session = Depends(get_session),
) -> Consulta:
    consulta = session.get(Consulta, consulta_id)
    if consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    return consulta


@consulta_router.post("/", response_model=Consulta, status_code=status.HTTP_201_CREATED)
async def criar_consulta(
    dados: ConsultaCreate,
    session: Session = Depends(get_session),
) -> Consulta:
    consulta = Consulta.model_validate(dados)
    session.add(consulta)
    session.commit()
    session.refresh(consulta)
    return consulta


@consulta_router.put("/{consulta_id}", response_model=Consulta)
async def atualizar_consulta(
    consulta_id: int,
    dados: ConsultaUpdate,
    session: Session = Depends(get_session),
) -> Consulta:
    consulta = session.get(Consulta, consulta_id)
    if consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    consulta.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.add(consulta)
    session.commit()
    session.refresh(consulta)
    return consulta


@consulta_router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_consulta(
    consulta_id: int,
    session: Session = Depends(get_session),
) -> Response:
    consulta = session.get(Consulta, consulta_id)
    if consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    session.delete(consulta)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
