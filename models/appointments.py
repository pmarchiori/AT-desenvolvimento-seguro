from datetime import datetime, timezone
from typing import Literal, Optional

from sqlmodel import Field, SQLModel
from models.base import StrictInputModel

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    professional_id: int = Field(foreign_key="user.id")
    date_time: datetime
    status: str = Field(default="agendada")
    notes: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

class AppointmentCreate(StrictInputModel):
    patient_id: int = Field(gt=0)
    date_time: datetime
    notes: Optional[str] = Field(default=None, max_length=500, regex=r"^[^<>]*$")

class AppointmentUpdate(StrictInputModel):
    patient_id: Optional[int] = Field(default=None, gt=0)
    date_time: Optional[datetime] = None
    status: Optional[Literal["agendada", "cancelada", "concluida"]] = None
    notes: Optional[str] = Field(default=None, max_length=500, regex=r"^[^<>]*$")

class AppointmentResponse(SQLModel):
    id: int
    patient_id: int
    professional_id: int
    date_time: datetime
    status: str
