from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from models.base import StrictInputModel

class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    cpf: str = Field(index=True, sa_column_kwargs={"unique": True})
    phone: str
    email: Optional[str] = None
    professional_id: Optional[int] = Field(default=None, foreign_key="user.id")

class PatientCreate(StrictInputModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        regex=r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$",
    )
    cpf: str = Field(regex=r"^\d{11}$")
    phone: str = Field(regex=r"^\d{10,11}$")
    email: Optional[EmailStr] = None
    professional_id: int = Field(gt=0)

class PatientResponse(SQLModel):
    id: int
    name: str
    professional_id: Optional[int]
