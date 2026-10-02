from typing import Literal, Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from models.base import StrictInputModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    password: str
    role: str = Field(default="recepcionista")

class UserCreate(StrictInputModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        regex=r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$",
    )
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserAdminCreate(UserCreate):
    role: Literal["admin", "recepcionista", "profissional"]

class MFARequest(StrictInputModel):
    mfa_token: str
    code: str = Field(regex=r"^\d{6}$")
