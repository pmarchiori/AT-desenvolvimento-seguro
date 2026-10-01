from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from auth.rbac import RoleChecker
from database.connection import get_session
from models.patients import Patient

patient_router = APIRouter(tags=["Patients"])
allow_manage_patients = RoleChecker(["admin", "recepcionista"])
allow_read_patients = RoleChecker(["admin", "recepcionista", "profissional"])

@patient_router.post("/new", response_model=Patient)
async def create_patient(
    patient: Patient,
    session: Session = Depends(get_session),
    current_user=Depends(allow_manage_patients),
):
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient

@patient_router.get("/", response_model=List[Patient])
async def get_all_patients(
    session: Session = Depends(get_session),
    current_user=Depends(allow_read_patients),
):
    return session.exec(select(Patient)).all()
