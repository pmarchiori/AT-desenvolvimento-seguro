from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from auth.rbac import RoleChecker
from database.connection import get_session
from models.appointments import Appointment
from models.users import User

def appointment_with_ownership(allowed_roles: list[str]):
    role_checker = RoleChecker(allowed_roles)

    async def check(
        appointment_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(role_checker),
    ) -> Appointment:
        appointment = session.get(Appointment, appointment_id)
        if appointment is None:
            raise HTTPException(status_code=404, detail="Consulta não encontrada")
        if (
            current_user.role == "profissional"
            and appointment.professional_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso permitido somente às próprias consultas",
            )
        return appointment
    return check
