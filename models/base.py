from sqlmodel import SQLModel

class StrictInputModel(SQLModel):
    class Config:
        extra = "forbid"

