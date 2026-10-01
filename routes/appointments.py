from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, func, select

from auth.rbac import RoleChecker
from database.connection import get_session
from models.appointments import Appointment, AppointmentCreate, AppointmentResponse, AppointmentUpdate
from models.users import User

appointment_router = APIRouter(tags=["Appointments"])
templates = Jinja2Templates(directory="templates")

allow_create = RoleChecker(["admin", "recepcionista"])
allow_read = RoleChecker(["admin", "recepcionista", "profissional"])
allow_manage = RoleChecker(["admin", "recepcionista"])

@appointment_router.post("/new", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_create),
):
    new_appointment = Appointment(**data.dict())
    session.add(new_appointment)
    session.commit()
    session.refresh(new_appointment)
    return new_appointment

@appointment_router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_read),
):
    return session.exec(select(Appointment)).all()

@appointment_router.get("/agenda")
async def show_daily_schedule(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_read),
):
    today = date.today()
    statement = select(Appointment).where(func.date(Appointment.date_time) == today.isoformat())
    appointments = session.exec(statement).all()
    return templates.TemplateResponse(
        "agenda.html",
        {"request": request, "appointments": appointments, "date": today},
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
    return appointment

@appointment_router.put("/edit/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_manage),
):
    appointment = session.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(appointment, key, value)
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment

@appointment_router.delete("/delete/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(allow_manage),
):
    appointment = session.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    session.delete(appointment)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
