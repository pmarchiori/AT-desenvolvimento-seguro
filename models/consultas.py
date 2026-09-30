from datetime import datetime

from sqlmodel import Field, SQLModel


class ConsultaBase(SQLModel):
    paciente_id: int
    profissional_id: int
    data_hora: datetime
    status: str


class Consulta(ConsultaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ConsultaCreate(ConsultaBase):
    pass


class ConsultaUpdate(SQLModel):
    paciente_id: int | None = None
    profissional_id: int | None = None
    data_hora: datetime | None = None
    status: str | None = None
