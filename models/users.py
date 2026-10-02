from typing import Literal, Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    password: str
    role: str = Field(default="recepcionista")

class UserCreate(SQLModel):
    name: str
    email: str
    password: str

class UserAdminCreate(UserCreate):
    role: Literal["admin", "recepcionista", "profissional"]

class MFARequest(SQLModel):
    mfa_token: str
    code: str
