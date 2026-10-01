from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

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

class AppointmentCreate(SQLModel):
    patient_id: int
    professional_id: int
    date_time: datetime
    notes: Optional[str] = None

class AppointmentUpdate(SQLModel):
    patient_id: Optional[int] = None
    professional_id: Optional[int] = None
    date_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(SQLModel):
    id: int
    patient_id: int
    professional_id: int
    date_time: datetime
    status: str
