import os
import secrets
from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session, func, select

from auth.jwt_handler import create_access_token
from auth.m2m import LAB_SCOPE, authenticate_laboratory
from database.connection import get_session
from models.appointments import Appointment


integration_router = APIRouter(tags=["External Integrations"])
basic_auth = HTTPBasic(auto_error=False)


@integration_router.post("/token")
async def create_machine_token(
    grant_type: str = Form(...),
    scope: str = Form(""),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    credentials: Optional[HTTPBasicCredentials] = Depends(basic_auth),
):
    supplied_id = credentials.username if credentials else client_id
    supplied_secret = credentials.password if credentials else client_secret
    expected_id = os.getenv("LAB_CLIENT_ID", "")
    expected_secret = os.getenv("LAB_CLIENT_SECRET", "")

    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="grant_type inválido")
    if not expected_id or not expected_secret:
        raise HTTPException(status_code=503, detail="Integração não configurada")
    if not supplied_id or not supplied_secret or not (
        secrets.compare_digest(supplied_id, expected_id)
        and secrets.compare_digest(supplied_secret, expected_secret)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais do cliente inválidas",
        )

    requested_scopes = set(scope.split()) if scope else {LAB_SCOPE}
    if not requested_scopes.issubset({LAB_SCOPE}):
        raise HTTPException(status_code=400, detail="Escopo inválido")

    access_token = create_access_token(
        supplied_id,
        actor_type="laboratory",
        scopes=sorted(requested_scopes),
    )
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": " ".join(sorted(requested_scopes)),
    }


@integration_router.get("/lab/availability")
async def get_available_slots(
    day: date,
    session: Session = Depends(get_session),
    token_data: dict = Depends(authenticate_laboratory),
):
    statement = select(Appointment).where(
        func.date(Appointment.date_time) == day.isoformat()
    )
    appointments = session.exec(statement).all()
    occupied = {appointment.date_time.replace(minute=0, second=0, microsecond=0) for appointment in appointments}
    slots = [
        datetime.combine(day, time(hour=hour))
        for hour in range(8, 18)
        if datetime.combine(day, time(hour=hour)) not in occupied
    ]
    return {
        "date": day,
        "available_slots": slots,
    }
