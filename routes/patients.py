from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from auth.rbac import RoleChecker
from database.connection import get_session
from models.patients import Patient, PatientCreate, PatientResponse

patient_router = APIRouter(tags=["Patients"])
allow_manage_patients = RoleChecker(["admin", "recepcionista"])
allow_read_patients = RoleChecker(["admin", "recepcionista", "profissional"])

@patient_router.post("/new", response_model=PatientResponse)
async def create_patient(
    data: PatientCreate,
    session: Session = Depends(get_session),
    current_user=Depends(allow_manage_patients),
):
    patient = Patient(**data.dict())
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient

@patient_router.get("/", response_model=List[PatientResponse])
async def get_all_patients(
    session: Session = Depends(get_session),
    current_user=Depends(allow_read_patients),
):
    statement = select(Patient)
    if current_user.role == "profissional":
        statement = statement.where(Patient.professional_id == current_user.id)
    return session.exec(statement).all()
