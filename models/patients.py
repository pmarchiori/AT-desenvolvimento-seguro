from typing import Optional

from sqlmodel import Field, SQLModel

class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    cpf: str = Field(index=True, sa_column_kwargs={"unique": True})
    phone: str
    email: Optional[str] = None
    professional_id: Optional[int] = Field(default=None, foreign_key="user.id")
