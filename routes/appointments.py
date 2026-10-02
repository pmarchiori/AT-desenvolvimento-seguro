from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, func, select

from auth.rbac import RoleChecker
from database.connection import get_session
from models.appointments import (
    Appointment,
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)
from models.patients import Patient
from models.users import User

appointment_router = APIRouter(tags=["Appointments"])
templates = Jinja2Templates(directory="templates")

allow_create = RoleChecker(["profissional"])
allow_read = RoleChecker(["admin", "recepcionista", "profissional"])
allow_manage = RoleChecker(["profissional"])

def ensure_ownership(appointment: Appointment, current_user: User) -> None:
    if (
        current_user.role == "profissional"
        and appointment.professional_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido somente às próprias consultas",
        )

def ensure_patient_ownership(
    patient_id: int,
    current_user: User,
    session: Session,
) -> None:
    patient = session.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    if patient.professional_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Paciente não está vinculado a este profissional",
        )

@appointment_router.post(
    "/new",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    data: AppointmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_create),
):
    ensure_patient_ownership(data.patient_id, current_user, session)
    appointment = Appointment(
        **data.dict(),
        professional_id=current_user.id,
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment

@appointment_router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_read),
):
    statement = select(Appointment)
    if current_user.role == "profissional":
        statement = statement.where(Appointment.professional_id == current_user.id)
    return session.exec(statement).all()

@appointment_router.get("/agenda")
async def show_daily_schedule(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_read),
):
    statement = select(Appointment).where(
        func.date(Appointment.date_time) == date.today().isoformat()
    )
    if current_user.role == "profissional":
        statement = statement.where(Appointment.professional_id == current_user.id)
    appointments = session.exec(statement).all()
    return templates.TemplateResponse(
        "agenda.html",
        {
            "request": request,
            "appointments": appointments,
            "date": date.today(),
        },
    )

@appointment_router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_read),
):
    appointment = session.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    ensure_ownership(appointment, current_user)
    return appointment

@appointment_router.put(
    "/edit/{appointment_id}",
    response_model=AppointmentResponse,
)
async def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_manage),
):
    appointment = session.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    ensure_ownership(appointment, current_user)

    update_data = data.dict(exclude_unset=True)
    if "patient_id" in update_data:
        ensure_patient_ownership(update_data["patient_id"], current_user, session)
    for key, value in update_data.items():
        setattr(appointment, key, value)
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment

@appointment_router.delete(
    "/delete/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_appointment(
    appointment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_manage),
):
    appointment = session.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    ensure_ownership(appointment, current_user)
    session.delete(appointment)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
